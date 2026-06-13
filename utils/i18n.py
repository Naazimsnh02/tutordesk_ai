"""UI string localization — button labels and headings per supported language.

Content localization (worksheet text, parent notes, etc.) lives in models/aya.py.
This file covers only static UI labels so the Gradio interface can reflect the
teacher's chosen language without an AI call.
"""
from __future__ import annotations

from config import CONFIG

SUPPORTED = CONFIG.languages

# Minimal label set. Extend as new UI strings are added.
_LABELS: dict[str, dict[str, str]] = {
    "English": {
        "generate": "Generate Teaching Pack",
        "grade": "Grade Answer Sheet",
        "translate": "Translate Content",
        "worksheet": "Worksheet",
        "homework": "Homework",
        "quiz": "Quiz",
        "answer_key": "Answer Key",
        "parent_note": "Parent Note",
        "download_pdf": "Download PDF",
    },
    "Hindi": {
        "generate": "शिक्षण सामग्री बनाएं",
        "grade": "उत्तर पत्रक जांचें",
        "translate": "सामग्री अनुवाद करें",
        "worksheet": "कार्यपत्रक",
        "homework": "गृहकार्य",
        "quiz": "प्रश्नोत्तरी",
        "answer_key": "उत्तर कुंजी",
        "parent_note": "अभिभावक नोट",
        "download_pdf": "PDF डाउनलोड करें",
    },
    "Tamil": {
        "generate": "கற்பித்தல் தொகுப்பை உருவாக்கு",
        "grade": "விடைத்தாள் மதிப்பீடு",
        "translate": "உள்ளடக்கத்தை மொழிபெயர்க்கவும்",
        "worksheet": "பணித்தாள்",
        "homework": "வீட்டுப்பாடம்",
        "quiz": "வினாடி வினா",
        "answer_key": "விடை திறவுகோல்",
        "parent_note": "பெற்றோர் குறிப்பு",
        "download_pdf": "PDF பதிவிறக்கவும்",
    },
}


def label(key: str, language: str = "English") -> str:
    """Return the UI label for `key` in `language`, falling back to English."""
    lang_labels = _LABELS.get(language, _LABELS["English"])
    return lang_labels.get(key, _LABELS["English"].get(key, key))
