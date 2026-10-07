import pandas as pd
import streamlit as st
import threading
import random
import json
import urllib.request
import streamlit.components.v1 as components
from fpdf import FPDF
import io
import time

# ================= SIDKONFIGURATION (MÅSTE VARA FÖRST) =================
st.set_page_config(
    page_title="GlosFlow - Digitala Glostränaren",
    page_icon="G",
    layout="wide"
)

# ================= SÄKERHET & LÄRARKONFIGURATION =================
# Hämtar i första hand lösenordet från st.secrets (säkert på GitHub/Streamlit Cloud)
# Finns det inte där används "skola123" som reservlösning.
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "skola123")

if "gsheets_url" not in st.session_state:
    st.session_state.gsheets_url = st.secrets.get(
        "GSHEETS_URL", 
        "https://script.google.com/macros/s/AKfycbx-CeGayXVPneyqfB-CNUzb4lrM-QejzQO96oJrjN0gMpUc1xDcVft_xbvrS8v6r9MC0w/exec"
    )

# ================= DATA: GLOSBIBLIOTEK =================
PERMANENT_LIBRARY = {
    "Glosor till v. 41": {
        "language": "Spanska",
        "category": "Spanska fortsättning",
        "words": [
            {"svenska": "Vad?, Vilken?, Vilka?", "utlandska": "¿Qué?"},
            {"svenska": "Hur?", "utlandska": "¿Cómo?"},
            {"svenska": "Var?", "utlandska": "¿Dónde?"},
            {"svenska": "När?", "utlandska": "¿Cuándo?"},
            {"svenska": "Varifrån?", "utlandska": "¿De dónde?"},
            {"svenska": "Vart?", "utlandska": "¿Adónde?"},
            {"svenska": "Varför?", "utlandska": "¿Por qué?"},
            {"svenska": "Hur mycket?", "utlandska": "¿Cuánto?"},
            {"svenska": "Hur många?", "utlandska": "¿Cuántos?, ¿Cuántas?"},
            {"svenska": "Vem?, Vilka? (endast om personer)", "utlandska": "¿Quién?, Quiénes?"},
            {"svenska": "Vilken?, Vem/vilka? (används vid urval)", "utlandska": "¿Cuál?, ¿Cuáles?"}
        ]
    },
    "Spanska nybörjare - v. 41": {
        "language": "Spanska",
        "category": "Spanska nybörjare",
        "words": [
            {"svenska": "att ha", "utlandska": "tener"},
            {"svenska": "jag har", "utlandska": "tengo"},
            {"svenska": "du har", "utlandska": "tienes"},
            {"svenska": "han/hon, den, har", "utlandska": "tiene"},
            {"svenska": "vi har", "utlandska": "tenemos"},
            {"svenska": "ni har", "utlandska": "tenéis"},
            {"svenska": "de, ni, har", "utlandska": "tienen"},
            {"svenska": "telefonnummer", "utlandska": "número de telefono"},
            {"svenska": "fråga", "utlandska": "pregunta"},
            {"svenska": "svara", "utlandska": "contesta"},
            {"svenska": "att behöva", "utlandska": "necesitar"},
            {"svenska": "att ringa", "utlandska": "llamar"}
        ]
    },
    "Spanska nybörjare - v. 38": {
        "language": "Spanska",
        "category": "Spanska nybörjare",
        "words": [
            {"svenska": "noll", "utlandska": "cero"},
            {"svenska": "ett", "utlandska": "uno"},
            {"svenska": "två", "utlandska": "dos"},
            {"svenska": "tre", "utlandska": "tres"},
            {"svenska": "fyra", "utlandska": "cuatro"},
            {"svenska": "fem", "utlandska": "cinco"},
            {"svenska": "sex", "utlandska": "seis"},
            {"svenska": "sju", "utlandska": "siete"},
            {"svenska": "åtta", "utlandska": "ocho"},
            {"svenska": "nio", "utlandska": "nueve"},
            {"svenska": "tio", "utlandska": "diez"},
            {"svenska": "hur mår du?", "utlandska": "¿cómo estás?"},
            {"svenska": "hur är läget?", "utlandska": "¿qué tal?"},
            {"svenska": "mycket bra, tack", "utlandska": "muy bien, gracias"},
            {"svenska": "och du?", "utlandska": "¿y tú?"}
        ]
    },
    "Spanska fortsättning - v. 38": {
        "language": "Spanska",
        "category": "Spanska fortsättning",
        "words": [
            {"svenska": "det är...", "utlandska": "hace..."},
            {"svenska": "det blåser", "utlandska": "hace viento"},
            {"svenska": "det är kallt", "utlandska": "hace frío"},
            {"svenska": "det är varmt", "utlandska": "hace calor"},
            {"svenska": "det är dåligt väder", "utlandska": "hace mal tiempo"},
            {"svenska": "det är bra väder", "utlandska": "hace buen tiempo"},
            {"svenska": "det är soligt", "utlandska": "hace sol"},
            {"svenska": "det är molnigt", "utlandska": "está nublado"},
            {"svenska": "det regnar", "utlandska": "llueve"},
            {"svenska": "det snöar", "utlandska": "nieva"},
            {"svenska": "vinter", "utlandska": "invierno"},
            {"svenska": "sommar", "utlandska": "verano"},
            {"svenska": "vår", "utlandska": "primavera"},
            {"svenska": "höst", "utlandska": "otoño"},
            {"svenska": "årstid", "utlandska": "estación"},
            {"svenska": "vad är det för väder?", "utlandska": "¿qué tiempo hace?"}
        ]
    },
    "Spanska nybörjare - till v. 37": {
        "language": "Spanska",
        "category": "Spanska nybörjare",
        "words": [
            {"svenska": "att vara", "utlandska": "ser"},
            {"svenska": "jag är", "utlandska": "yo soy"},
            {"svenska": "du är", "utlandska": "tú eres"},
            {"svenska": "han/hon är", "utlandska": "él/ella es"},
            {"svenska": "vad heter du?", "utlandska": "¿Cómo te llamas?"},
            {"svenska": "Jag heter...", "utlandska": "Me llamo..."},
            {"svenska": "Jag är från...", "utlandska": "Soy de"},
            {"svenska": "Han/hon är från...", "utlandska": "Es de..."},
            {"svenska": "Sverige", "utlandska": "Suecia"},
            {"svenska": "jag pratar/talar", "utlandska": "hablo"},
            {"svenska": "svenska", "utlandska": "sueco"},
            {"svenska": "spanska", "utlandska": "español"},
            {"svenska": "engelska", "utlandska": "inglés"},
            {"svenska": "Var är du från?", "utlandska": "¿De dónde eres?"},
            {"svenska": "Vilka språk talar du?", "utlandska": "¿Qué lenguas hablas?"}
        ]
    },
    "Spanska fortsättning - v. 37": {
        "language": "Spanska",
        "category": "Spanska fortsättning",
        "words": [
            {"svenska": "vilket datum är det idag?", "utlandska": "¿qué fecha es hoy?"},
            {"svenska": "måndag", "utlandska": "lunes"},
            {"svenska": "tisdag", "utlandska": "martes"},
            {"svenska": "onsdag
