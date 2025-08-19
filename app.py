import streamlit as st
import pandas as pd
import seaborn as sns
import random
from openai import OpenAI
from dotenv import dotenv_values
from config.constants import APP_TITLE, BIG5_ITEMS

# Set the page configuration
st.set_page_config(
    page_title="Big Five Personality Test",
    page_icon="🧠",
    layout="centered",  # Options: "centered" or "wide"
    initial_sidebar_state="expanded"  # Options: "auto", "expanded", "collapsed"
)

# Your app code here
st.title(f"🧠 {APP_TITLE}")

big5_items = BIG5_ITEMS

env = dotenv_values(".env")

openai_client = OpenAI(api_key=env.get("OPENAI_API_KEY"))

if "results" not in st.session_state:
    st.session_state.results = None


def get_person_description(results: dict):
    personality_description = openai_client.chat.completions.create(
        model="gpt-4o-mini",
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
                # "Nie dodawaj żadnego komentarza, tekstu ani wyjaśnienia poza JSON-em. "
                # # "Struktura odpowiedzi musi być dokładnie taka:"
                # # # "{"
                # # # "  \"opis\": \"string\","
                # # # "  \"mocne_strony\": [\"string\", \"string\"],"
                # # # "  \"obszary_rozwoju\": [\"string\", \"string\"],"
                # # # "  \"kompetencje_miekkie\": [\"string\", \"string\"],"
                # # # "  \"frazy_do_cv\": [\"string\", \"string\"]"
                # # # "  \"opis_do_CV\": \"string\","
                # # # "}"
                "W JSON zawsze używaj stałych nazw kluczy - opis_osobowosci, mocne_strony, obszary_rozwoju, kompetencje_miekkie, frazy_do_cv, opis_do_cv"

            )
        },
        {
            "role": "user",
            "content": f"Użytkownik uzyskał następujące wyniki w teście: {results}"
        }
        ]
    )
    return personality_description.choices[0].message.content

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

def show_results(results: dict):
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

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="TOP-1", value=results["top3"][0][0])
    with col2:
        st.metric(label="TOP-2", value=results["top3"][1][0])
    with col3:
        st.metric(label="TOP-3", value=results["top3"][2][0])

    st.markdown("---")

    with st.spinner("Generuję opis..."):
        description = get_person_description(results)   
    st.markdown(description)

with st.sidebar:
    st.title("🧠 Big Five Personality Test")
    st.write("Witaj w teście Big Five Personality!")
    st.write("Ten test pomaga zrozumieć, jakie umiejętności i cechy charakteru posiadasz.")
    st.write("Odpowiedz na pytania, a dowiesz się, jakie masz cechy charakteru.")

if st.sidebar.button("Losuj odpowiedzi"):
    responses = random_responses(big5_items)
    st.session_state.results = score_big5(responses)
    show_results(st.session_state.results)
    
    
# --- Przykład użycia ---
# responses = random_responses(big5_items)
# print("Symulowane odpowiedzi:", responses)

# results = score_big5(responses)
# print("\nWyniki procentowe:", results["percent"])
# print("Etykiety:", results["labels"])
# print("TOP-3:", results["top3"])


#
# Wyróżnianie danych
#

st.success("✅ To jest pozytywny komunikat w zielonym boxie.")
st.info("ℹ️ To jest informacyjny box w niebieskim kolorze.")
st.warning("⚠️ To jest ostrzeżenie w żółtym boxie.")
st.error("❌ To jest komunikat błędu w czerwonym boxie.")

with st.container():
    st.write("### 📌 To jest nagłówek w boxie")
    st.write("Tutaj możesz wrzucić więcej treści, np. wykresy lub metryki.")

with st.status("Analiza wyników Big Five", expanded=True) as status:
    st.write("🔍 Przetwarzanie danych użytkownika...")
    st.write("📊 Generowanie wykresów...")
    st.write("✅ Gotowe!")