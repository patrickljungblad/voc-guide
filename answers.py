"""Rättning som bevarar betydelseskiljande tecken, t.ex. ñ och å."""
import re
import unicodedata
from difflib import SequenceMatcher


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text).casefold().strip()
    text = text.replace("…", "...")
    return re.sub(r"\s+", " ", text).strip("¿?¡!.,;: ")


def without_accents(text: str) -> str:
    # ñ, å, ä, ö är egna bokstäver: de får inte bli ett korrekt annat ord.
    return text.translate(str.maketrans("áéíóúàèìòù", "aeiouaeiou"))


def grade(answer: str, accepted: list[str]) -> tuple[str, str]:
    value = normalize(answer)
    candidates = [(normalize(x), x) for x in accepted]
    for clean, original in candidates:
        if value and value == clean:
            return "correct", original
    for clean, original in candidates:
        if value and without_accents(value) == without_accents(clean):
            return "near", original
    # Små stavfel ger återkoppling, aldrig godkännande eller avancemang.
    for clean, original in candidates:
        if len(clean) >= 5 and value and SequenceMatcher(None, value, clean).ratio() >= .86:
            return "near", original
    return "wrong", accepted[0]
