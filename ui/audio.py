"""Uppläsning i webbläsaren: inga ljudanrop till appens databas."""
import json
import re
from pathlib import Path
import streamlit.components.v1 as components

LANGUAGES = {"spanska": "es-MX", "spanish": "es-MX", "español": "es-MX",
             "engelska": "en-GB", "english": "en-GB", "svenska": "sv-SE",
             "swedish": "sv-SE", "franska": "fr-FR", "french": "fr-FR",
             "tyska": "de-DE", "german": "de-DE", "italienska": "it-IT",
             "portugisiska": "pt-BR", "danska": "da-DK", "norska": "nb-NO"}


def language_tag(language):
    value = language.strip()
    if value.casefold() in LANGUAGES:
        return LANGUAGES[value.casefold()]
    if re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z]{2,4})?", value):
        return value
    return None


def speech_html(rows, language, table=False):
    payload = json.dumps({"rows": rows, "language": language_tag(language),
                          "label": language, "table": table}, ensure_ascii=False)
    # Ord och listnamn får aldrig kunna avsluta script-taggen.
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = Path(__file__).with_name("speech.html").read_text(encoding="utf-8")
    return template.replace("__SPEECH_DATA__", payload)


def listen(text, language):
    components.html(speech_html([{"target": [text]}], language),
                    height=min(420, 160 + (len(text) // 30) * 24), scrolling=True)


def word_table(words, language):
    rows = [{"svenska": w["svenska"], "target": w["accepted_answers"]} for w in words]
    components.html(speech_html(rows, language, table=True),
                    height=min(660, 190 + 92 * len(rows)), scrolling=True)
