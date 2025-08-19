from typing import Final

APP_TITLE: Final[str] = "Big Five - Interpretacja wyników"

BIG5_ITEMS: Final[dict[str, list[dict[str, str]]]] = {
    "O": [  # Otwartość
        {"id": "O1", "text": "Lubię odkrywać nowe pomysły i podejścia.", "reverse": False, "weight": 1.0},
        {"id": "O2", "text": "Interesuję się sztuką lub kulturą.",         "reverse": False, "weight": 1.0},
        {"id": "O3", "text": "Nowe doświadczenia są dla mnie atrakcyjne.",  "reverse": False, "weight": 1.0},
        {"id": "O4", "text": "Raczej trzymam się utartych schematów.",      "reverse": True,  "weight": 1.0},
    ],
    "C": [  # Sumienność
        {"id": "C1", "text": "Kończę rozpoczęte zadania.",                  "reverse": False, "weight": 1.0},
        {"id": "C2", "text": "Planuję pracę z wyprzedzeniem.",              "reverse": False, "weight": 1.0},
        {"id": "C3", "text": "Dbam o szczegóły i terminowość.",             "reverse": False, "weight": 1.0},
        {"id": "C4", "text": "Często odkładam obowiązki na później.",       "reverse": True,  "weight": 1.0},
    ],
    "E": [  # Ekstrawersja
        {"id": "E1", "text": "Spotkania z ludźmi dodają mi energii.",       "reverse": False, "weight": 1.0},
        {"id": "E2", "text": "Łatwo nawiązuję kontakty towarzyskie.",       "reverse": False, "weight": 1.0},
        {"id": "E3", "text": "Lubię być w centrum wydarzeń.",               "reverse": False, "weight": 1.0},
        {"id": "E4", "text": "Preferuję unikać towarzystwa, gdy mogę.",     "reverse": True,  "weight": 1.0},
    ],
    "A": [  # Ugodowość
        {"id": "A1", "text": "Chętnie współpracuję i szukam porozumienia.", "reverse": False, "weight": 1.0},
        {"id": "A2", "text": "Potrafię znaleźć kompromis w sporach.",       "reverse": False, "weight": 1.0},
        {"id": "A3", "text": "Naturalnie okazuję życzliwość innym.",        "reverse": False, "weight": 1.0},
        {"id": "A4", "text": "Często idę na konfrontację zamiast ustępstw.", "reverse": True, "weight": 1.0},
    ],
    "N": [  # Neurotyczność
        {"id": "N1", "text": "Łatwo odczuwam stres w wymagających sytuacjach.", "reverse": False, "weight": 1.0},
        {"id": "N2", "text": "Mam skłonność do zamartwiania się drobiazgami.",  "reverse": False, "weight": 1.0},
        {"id": "N3", "text": "Często doświadczam napięcia lub niepokoju.",      "reverse": False, "weight": 1.0},
        {"id": "N4", "text": "Zwykle zachowuję spokój niezależnie od okoliczności.", "reverse": True, "weight": 1.0},
    ]
}

BIG5_SHORT_LABELS = {
    "O": "Otwartość na doświadczenie",
    "C": "Sumienność",
    "E": "Ekstrawersja",
    "A": "Ugodowość",
    "N": "Neurotyczność"
}



