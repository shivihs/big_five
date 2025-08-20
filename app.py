import streamlit as st
import random
from openai import OpenAI
from dotenv import dotenv_values
from config.constants import APP_TITLE, BIG5_ITEMS, BIG5_SHORT_LABELS
import json

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧠",
    layout="centered",  
    initial_sidebar_state="expanded"  
)

st.header(f"🧠 {APP_TITLE} :computer:")

big5_items = BIG5_ITEMS

# Initialize API key handling
api_key = None

# Try to get API key from Streamlit secrets
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.sidebar.success("✅ Używam klucza API z ustawień Streamlit")
except Exception as e:
    st.sidebar.warning("⚠️ Nie znaleziono klucza API w ustawieniach Streamlit")

# If no API key in secrets, try .env file
if not api_key:
    try:
        env = dotenv_values(".env")
        api_key = env.get("OPENAI_API_KEY")
        if api_key:
            st.sidebar.success("✅ Używam klucza API z pliku .env")
    except Exception as e:
        st.sidebar.warning("⚠️ Nie znaleziono pliku .env lub brak w nim klucza API")

# If still no API key, ask user
if not api_key:
    st.sidebar.info("ℹ️ Podaj swój klucz OpenAI API poniżej")
    api_key = st.sidebar.text_input("Klucz OpenAI API", type="password")

# Validate and store API key
if api_key:
    if len(api_key.strip()) < 20:  # Basic validation
        st.sidebar.error("❌ Nieprawidłowy format klucza API")
        st.stop()
    st.session_state["openai_api_key"] = api_key.strip()
else:
    st.sidebar.error("❌ Brak klucza API - aplikacja nie będzie działać")
    st.stop()

def get_openai_client():
    if not st.session_state.get("openai_api_key"):
        st.error("❌ Brak klucza API w session_state")
        st.stop()
    try:
        client = OpenAI(api_key=st.session_state["openai_api_key"])
        return client
    except Exception as e:
        st.error(f"❌ Błąd podczas tworzenia klienta OpenAI: {str(e)}")
        st.stop()

# Create OpenAI client
try:
    openai_client = get_openai_client()
    st.sidebar.success("✅ Połączono z OpenAI API")
except Exception as e:
    st.sidebar.error(f"❌ Nie udało się połączyć z OpenAI API: {str(e)}")
    st.stop()

if "results" not in st.session_state:
    st.session_state.results = None


def get_person_description(results: dict):
    try:
        personality_description = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
            {
                "role": "system",
                "content": (
                    "Jesteś pomocnym asystentem, który tworzy opis osobowości użytkownika "
                    "na podstawie wyników Testu Wielkiej Piątki (Big Five). "
                    "Twoim zadaniem jest:\n"
                    "- przedstawić opis w zrozumiałym i przyjaznym języku,\n"
                    "- podkreślić mocne strony użytkownika,\n"
                    "- wskazać potencjalne obszary do rozwoju,\n"
                    "- wygenerować listę kluczowych kompetencji miękkich,\n"
                    "- zaproponować 2–3 przykładowe frazy, które użytkownik może wykorzystać w CV.\n"
                    "Jako podsumowanie podaj opis kompetencji miękkich w 4-5 zdaniach pisanych w pierwszej osobie do CV - unikaj z testu, pisz naturalnie jako osoba nie znająca nomenklatury psychologicznej..\n"
                    "Zawsze odpowiadaj wyłącznie w formacie JSON. "
                    "W JSON zawsze używaj stałych nazw kluczy - opis_osobowosci (string), mocne_strony (lista stringów), obszary_rozwoju (lista stringów), kompetencje_miekkie (lista stringów), frazy_do_cv (lista stringów), opis_do_cv (string)"
                )
            },
            {
                "role": "user",
                "content": f"Użytkownik uzyskał następujące wyniki w teście: {results}"
            }
            ]
        )
        response_content = personality_description.choices[0].message.content
        # Sprawdź, czy odpowiedź jest poprawnym JSON
        try:
            json.loads(response_content)
            return response_content
        except json.JSONDecodeError:
            st.error("BLAD: Otrzymano niepoprawna odpowiedz od API (nieprawidlowy format JSON)")
            st.stop()
    except Exception as e:
        st.error(f"BLAD: Problem podczas generowania opisu: {str(e)}")
        st.stop()

def score_item(answer_1_to_5: int, reverse: bool) -> float:
    """Zwraca wynik w skali 1–5 po uwzględnieniu odwrócenia."""
    answer_1_to_5 = max(1, min(5, int(answer_1_to_5)))
    return 6 - answer_1_to_5 if reverse else answer_1_to_5

def trait_percent(trait_scores_1_to_5: list[float]) -> float:
    """Przelicza średnią 1–5 na % (0–100)."""
    if not trait_scores_1_to_5:
        return 0.0
    mean = sum(trait_scores_1_to_5) / len(trait_scores_1_to_5)
    return round(((mean - 1) / 4) * 100, 1)

def intensity_label(pct: float) -> str:
    """Etykieta natężenia do generowania języka opisu."""
    if pct >= 80:
        return "wysoka"
    if pct >= 60:
        return "podwyższona"
    if pct >= 40:
        return "zrównoważona"
    return "niska"

def score_big5(responses: dict[str, int]) -> dict:
    """
    responses: dict mapujący ID pozycji -> odpowiedź 1–5, np. {"O1": 4, "O2": 5, ...}
    Zwraca słownik: procenty cech, etykiety natężenia oraz TOP-3.
    """
    trait_values = {}
    for trait, items in big5_items.items():
        scores = []
        for it in items:
            ans = responses.get(it["id"])
            if ans is None:
                continue
            scores.append(score_item(ans, it["reverse"]) * it["weight"])
        trait_values[trait] = trait_percent(scores) if scores else 0.0

    labels = {t: intensity_label(p) for t, p in trait_values.items()}
    top3 = sorted(trait_values.items(), key=lambda kv: kv[1], reverse=True)[:3]

    return {
        "percent": trait_values,   # np. {"O": 72.5, "C": 81.2, ...}
        "labels": labels,          # np. {"O": "podwyższona", ...}
        "top3": top3               # lista par [("C", 81.2), ("E", 73.0), ("O", 72.5)]
    }

def random_responses(big5_items: dict) -> dict[str, int]:
    """
    Generuje losowe odpowiedzi 1–5 dla wszystkich pytań Big5.
    Zwraca dict: {"O1": 3, "O2": 5, ...}
    """
    responses = {}
    for trait, items in big5_items.items():
        for it in items:
            responses[it["id"]] = random.randint(1, 5)
    return responses

def show_big5_results(description: dict):
    st.markdown(description["opis_osobowosci"])

def show_list(items):
    if not items:
        return
    # Upewnij się, że items to lista
    if isinstance(items, str):
        # Jeśli to string, spróbuj go rozdzielić lub potraktuj jako pojedynczy element
        items = [items] if items else []
    elif not isinstance(items, list):
        items = []
    
    bullets = "\n".join([f"- {item}" for item in items])
    st.markdown(bullets)

def show_description(description: dict):
    st.subheader("Opis Twoich cech charakteru:")
    st.success(description["opis_osobowosci"])
    with st.status("Mocne strony"):
        show_list(description["mocne_strony"])
    with st.status("Obszary rozwoju"):
        show_list(description["obszary_rozwoju"])
    with st.status("Kompetencje miękkie"):
        show_list(description["kompetencje_miekkie"])
    with st.status("Frazy do CV"):
        show_list(description["frazy_do_cv"])
    st.subheader("Propozycja opisu do CV:")
    st.info(description["opis_do_cv"])

def show_results(results: dict):

    st.markdown("---")
    st.subheader("Twoje wyniki w teście Big Five Personality:\n\n")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Otwartość na doświadczenie", value=results["percent"]["O"])
    with col2:
        st.metric(label="Sumienność", value=results["percent"]["C"])
    with col3:
        st.metric(label="Ekstrawersja", value=results["percent"]["E"])
    with col4:
        st.metric(label="Ugodowość", value=results["percent"]["A"])
    with col5:
        st.metric(label="Neurotyczność", value=results["percent"]["N"])

    st.markdown("---")

    st.subheader("Twoje TOP-3 cechy charakteru:")
    st.markdown(f"""
    - {BIG5_SHORT_LABELS[results["top3"][0][0]]} - {results["top3"][0][1]}%
    - {BIG5_SHORT_LABELS[results["top3"][1][0]]} - {results["top3"][1][1]}%
    - {BIG5_SHORT_LABELS[results["top3"][2][0]]} - {results["top3"][2][1]}%
    """)

    st.markdown("---")
    description = None
    with st.spinner("Generuję opis..."):
        description = json.loads(get_person_description(st.session_state.results))   
    
    show_description(description)



with st.sidebar:
    st.subheader(":blue[**Witaj w teście Big Five (IPP20)!**]")
    st.markdown("Ten test nie jest diagnozą – to narzędzie, które pomoże Ci lepiej poznać siebie.")
    st.markdown("Dzięki niemu zobaczysz swoje atuty, zauważysz obszary do rozwoju i otrzymasz propozycję, jak możesz ująć swoje mocne strony w CV.")
    st.markdown("**Traktuj wyniki jako podpowiedź i inspirację, a nie ostateczną ocenę.**")

if st.sidebar.button("Losuj odpowiedzi"):       
    responses = random_responses(big5_items)
    st.session_state.results = score_big5(responses)
    show_results(st.session_state.results)



