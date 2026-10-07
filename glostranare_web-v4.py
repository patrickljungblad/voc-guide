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
            {"svenska": "onsdag", "utlandska": "miércoles"},
            {"svenska": "torsdag", "utlandska": "jueves"},
            {"svenska": "fredag", "utlandska": "viernes"},
            {"svenska": "lördag", "utlandska": "sábado"},
            {"svenska": "söndag", "utlandska": "domingo"},
            {"svenska": "januari", "utlandska": "enero"},
            {"svenska": "februari", "utlandska": "febrero"},
            {"svenska": "mars", "utlandska": "marzo"},
            {"svenska": "april", "utlandska": "abril"},
            {"svenska": "maj", "utlandska": "mayo"},
            {"svenska": "juni", "utlandska": "junio"},
            {"svenska": "juli", "utlandska": "julio"},
            {"svenska": "augusti", "utlandska": "agosto"},
            {"svenska": "september", "utlandska": "septiembre"},
            {"svenska": "oktober", "utlandska": "octubre"},
            {"svenska": "november", "utlandska": "noviembre"},
            {"svenska": "december", "utlandska": "diciembre"}
        ]
    },
    "Spanska nybörjare - v. 36": {
        "language": "Spanska",
        "category": "Spanska nybörjare",
        "words": [
            {"svenska": "bok", "utlandska": "libro"},
            {"svenska": "blyertspenna", "utlandska": "lápiz"},
            {"svenska": "bläckpenna", "utlandska": "bolígrafo"},
            {"svenska": "skrivhäfte", "utlandska": "cuaderno"},
            {"svenska": "ett papper (pappersark)", "utlandska": "hoja de papel"},
            {"svenska": "ryggsäck", "utlandska": "mochila"},
            {"svenska": "skåp", "utlandska": "casilla"},
            {"svenska": "dator", "utlandska": "computadora, ordenador"},
            {"svenska": "laddare", "utlandska": "cargador"},
            {"svenska": "sudd", "utlandska": "goma"},
            {"svenska": "surfplatta", "utlandska": "tableta"},
            {"svenska": "tavla", "utlandska": "pizarra"},
            {"svenska": "god morgon/god dag", "utlandska": "buenos días"},
            {"svenska": "hej då, farväl", "utlandska": "adios"},
            {"svenska": "jag är här", "utlandska": "estoy aquí"},
            {"svenska": "elever", "utlandska": "alumnos"}
        ]
    },
    "Spanska fortsättning - v. 36": {
        "language": "Spanska",
        "category": "Spanska fortsättning",
        "words": [
            {"svenska": "på min fritid brukar jag...", "utlandska": "en mi tiempo libre suelo..."},
            {"svenska": "vara med mina vänner", "utlandska": "estar con mis amigos"},
            {"svenska": "spela ett instrument", "utlandska": "tocar un instrumento"},
            {"svenska": "spela tv-spel", "utlandska": "jugar a videojuegos"},
            {"svenska": "surfa på nätet, surfa på internet", "utlandska": "navegar por la red/internet"},
            {"svenska": "rida", "utlandska": "montar a caballo"},
            {"svenska": "gå ut med hunden", "utlandska": "salir con el perro"},
            {"svenska": "åka till centrum, gå till centrum", "utlandska": "ir al centro"},
            {"svenska": "läsa böcker", "utlandska": "leer libros"},
            {"svenska": "rita, teckna", "utlandska": "dibujar"},
            {"svenska": "plugga, studera", "utlandska": "estudiar"},
            {"svenska": "chatta", "utlandska": "chatear"},
            {"svenska": "arbeta, jobba", "utlandska": "trabajar"},
            {"svenska": "sova", "utlandska": "dormir"},
            {"svenska": "vila", "utlandska": "descansar"},
            {"svenska": "laga mat", "utlandska": "cocinar"},
            {"svenska": "dansa", "utlandska": "bailar"},
            {"svenska": "träna", "utlandska": "entrenar"},
            {"svenska": "titta på film", "utlandska": "mirar películas"},
            {"svenska": "spela fotboll", "utlandska": "jugar al fútbol"}
        ]
    }
}

# ================= FUNKTIONER: STRATEGIER & PEDAGOGIK =================
def clean_html(html_str):
    return "\n".join(line.strip() for line in html_str.split("\n"))

def get_strategy_tip(word_obj, language):
    sv = word_obj["svenska"].lower().strip()
    ut = word_obj["utlandska"].lower().strip()
    
    # Custom spanska nyckelordstips (Mnemonic Keyword Technique)
    spanish_tips = {
        "ser": "**Associationstips:** *ser* är grundformen för att vara på spanska. Tänk på ordet *seriös* eller engelskans *series*.",
        "suecia": "**Kognat-tips:** *Suecia* låter nästan som *Sverige* på franska (*Suède*) eller engelska (*Sweden*)!",
        "español": "**Kognat-tips:** *español* är väldigt likt svenskans spanska och engelskans *Spanish*.",
        "inglés": "**Kognat-tips:** *inglés* är superlikt *engelska* (eller franskans *anglais*).",
        "hablo": "**Associationstips:** *hablo* kommer från *hablar* (att prata). Tänk på 'hävla ur sig' ord eller engelskans *babble*.",
        "lunes": "**Etymologitips:** *lunes* kommer från latinets *luna* (måne). Måndag är helt enkelt 'måndagen'!",
        "martes": "**Etymologitips:** *martes* är uppkallat efter krigsguden Mars. På svenska är tisdag uppkallad efter vår krigsgud Tyr!",
        "miércoles": "**Etymologitips:** *miércoles* är uppkallat efter budbäraren och handelsguden Merkurius.",
        "jueves": "**Etymologitips:** *jueves* är uppkallat efter dunder- och blixtguden Jupiter. På svenska är torsdag Tors dag – en klockren koppling!",
        "viernes": "**Etymologitips:** *viernes* är uppkallat efter kärleksgudinnan Venus. På svenska är det Frejas dag – båda hyllar kärleken!",
        "sábado": "**Associationstips:** *sábado* är nära besläktat med ordet *sabbat* (vilodag). Det är lördag och dags för vila!",
        "domingo": "**Associationstips:** *domingo* kommer från latinets *dominus* (herre) och betyder 'herrens dag'. Tänk på att dominera!",
        "att ha": "**Grammatiktips:** *tener* är grundformen för 'att ha' på spanska.",
        "jag har": "**Grammatiktips:** *yo tengo* = jag har. Slutar på *-o* som nästan alla 'jag'-former på spanska!",
        "telefonnummer": "**Kognat-tips:** *número de teléfono* låter nästan exakt som nummer och telefon på svenska!",
        "fråga": "**Associationstips:** *pregunta* – tänk på att 'pruta' eller ställa frågor inför ett köp.",
        "svara": "**Associationstips:** *contesta* låter som engelskans *contestant* (en tävlande som svarar på frågor).",
        "bok": "**Nyckelordstips:** *libro* låter lite som engelskans *library* (bibliotek) eller spanskans *libre* (fri). Föreställ dig en fri bok som flyger ut genom fönstret!",
        "blyertspenna": "**Nyckelordstips:** *lápiz* låter som *lapis* (blå sten) eller som att 'lappa'.",
        "dator": "**Kognat-tips:** *computadora* är nästan identiskt med engelskans *computer*. Enkel kognat! *Ordenador* låter som att 'ordna' – datorn ordnar dina filer.",
        "hund": "**Nyckelordstips:** *perro* låter lite som *pärla*. Föreställ dig en fluffig hund som bär ett glittrande pärlhalsband!",
        "katt": "**Kognat-tips:** *gato* är besläktat med engelskans *cat* och tyskans *Katze*. Tänk dig en katt i en hög svart hatt!",
        "det är kallt": "**Associationstips:** *hace frío* – *frío* är jättenära svenskans *frysa* och engelskans *freezing*! Lätt att koppla till kyla.",
        "det är soligt": "**Kognat-tips:** *hace sol* – *sol* stavas och betyder exakt samma sak på spanska som på svenska! Superlätt kognat.",
    }
    
    english_tips = {
        "tid": "**Kognat-tips:** *time* stavas nästan som tid och uttalas nästan likadant!",
        "år": "**Associationstips:** *year* – tänk på nyår (*New Year*) eller födelsedag (*birthday*).",
        "skola": "**Kognat-tips:** *school* är mycket likt svenska skola! Enkel kognat.",
        "familj": "**Kognat-tips:** *family* är mycket likt svenskans familj. Enkel kognat."
    }
    
    if language.lower() == "spanska":
        if sv in spanish_tips: return spanish_tips[sv]
        if ut in spanish_tips: return spanish_tips[ut]
    elif language.lower() == "engelska" and sv in english_tips:
        return english_tips[sv]
    
    return f"**Nyckelordsmetoden:** Prova att hitta ett svenskt ord som låter som det utländska ordet '{ut}'. Föreställ dig sedan en rolig eller konstig bild i huvudet där det ordet kopplas ihop med betydelsen '{sv}'! Det hjälper hjärnan att bygga en stark form-betydelse-bro."

# ================= FUNKTIONER: PDF OCH UTSKRIFT =================
def generate_study_list_pdf_bytes(words_list, list_title, target_lang_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margin(15)
    
    def safe_pdf_str(text):
        if not isinstance(text, str): text = str(text)
        text = text.replace("➔", "->").replace("¿", "").replace("¡", "").replace("—", "-")
        return text.encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("helvetica", "B", size=18)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(w=0, h=10, text=safe_pdf_str(f"Gloslista: {list_title}"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "I", size=10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(w=0, h=6, text=safe_pdf_str(f"Språk: {target_lang_name}  |  Antal glosor: {len(words_list)}"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    pdf.set_draw_color(16, 185, 129)
    pdf.set_line_width(0.8)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(10)
    
    pdf.set_draw_color(226, 232, 240)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font("helvetica", "B", size=11)
    pdf.set_text_color(15, 23, 42)
    
    pdf.cell(w=12, h=8, text="Nr", border=1, fill=True)
    pdf.cell(w=74, h=8, text=safe_pdf_str("Svenska"), border=1, fill=True)
    pdf.cell(w=74, h=8, text=safe_pdf_str(target_lang_name), border=1, fill=True)
    pdf.cell(w=20, h=8, text=safe_pdf_str("[ ] Övad"), border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", size=10)
    for idx, w in enumerate(words_list, 1):
        sv = safe_pdf_str(w.get("svenska", ""))
        ut = safe_pdf_str(w.get("utlandska", ""))
        pdf.set_text_color(30, 41, 59)
        pdf.cell(w=12, h=8, text=f"{idx}.", border="B")
        pdf.cell(w=74, h=8, text=sv, border="B")
        pdf.cell(w=74, h=8, text=ut, border="B")
        pdf.set_text_color(148, 163, 184)
        pdf.cell(w=20, h=8, text="[   ]", border="B", new_x="LMARGIN", new_y="NEXT")
        
    return pdf.output()

def generate_study_list_html(words_list, list_title, target_lang_name):
    style_block = """
    <style>
    @media print {
        header, footer, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stToolbar"], .stTabs, button, hr, .print-hide {
            display: none !important;
        }
        body, .stApp, .main, .block-container, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
            height: auto !important;
            overflow: visible !important;
            padding: 0 !important;
            margin: 0 !important;
            display: block !important;
        }
        body * { visibility: hidden !important; }
        .print-container, .print-container * { visibility: visible !important; }
        .print-container {
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
    }
    .print-container {
        background-color: white; color: black; padding: 30px; border: 1px solid #e2e8f0;
        border-radius: 8px; font-family: sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .print-title { font-size: 24px; font-weight: bold; text-align: center; color: #1e3a8a; margin-bottom: 5px; }
    .print-subtitle { font-size: 14px; text-align: center; color: #64748b; margin-bottom: 20px; }
    .study-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .study-table th { background-color: #f1f5f9; text-align: left; padding: 10px; border-bottom: 2px solid #cbd5e1; }
    .study-table td { padding: 10px; border-bottom: 1px solid #e2e8f0; }
    .study-num { width: 40px; font-weight: bold; color: #475569; }
    .check-box { width: 60px; text-align: center; color: #94a3b8; }
    </style>
    """
    
    html = style_block + "<div class='print-container'>"
    html += f"<div class='print-title'>GLOSLISTA: {list_title}</div>"
    html += f"<div class='print-subtitle'>Språk: {target_lang_name} • Antal glosor: {len(words_list)}</div>"
    html += """<table class='study-table'><thead><tr><th class='study-num'>Nr</th><th>Svenska</th>"""
    html += f"<th>{target_lang_name}</th><th class='check-box'>Övad</th></tr></thead><tbody>"
    for idx, w in enumerate(words_list, 1):
        sv = w.get("svenska", "")
        ut = w.get("utlandska", "")
        html += f"<tr><td class='study-num'>{idx}.</td><td><b>{sv}</b></td><td>{ut}</td><td class='check-box'>☐</td></tr>"
    html += "</tbody></table></div>"
    return html

def generate_pdf_bytes(test_words, quiz_title, target_lang_name, include_answers):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margin(20)
    pdf.set_draw_color(16, 185, 129)
    pdf.set_font("helvetica", "B", size=20)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(w=0, h=12, text=quiz_title, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(8)
    pdf.set_text_color(51, 65, 85)
    pdf.set_font("helvetica", size=11)
    pdf.cell(w=20, h=8, text="Namn:")
    pdf.cell(w=60, h=8, border="B", text="")
    pdf.cell(w=10, h=8, text="")
    pdf.cell(w=25, h=8, text="Klass/Grupp:")
    pdf.cell(w=45, h=8, border="B", text="")
    pdf.ln(10)
    pdf.cell(w=15, h=8, text="Datum:")
    pdf.cell(w=45, h=8, border="B", text="")
    pdf.cell(w=10, h=8, text="")
    pdf.set_font("helvetica", "B", size=11)
    pdf.cell(w=0, h=8, text=f"Poäng: ________ av {len(test_words)} rätt", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(12)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_font("helvetica", "B", size=12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w=15, h=8, text="Nr", border="B")
    pdf.cell(w=80, h=8, text="Svenska / Glosa", border="B")
    pdf.cell(w=75, h=8, text="Översättning", border="B", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("helvetica", size=11)
    pdf.set_text_color(51, 65, 85)
    for idx, w in enumerate(test_words, 1):
        p_word = w.get("prompt_word", w["svenska"]).replace("➔", "->")
        pdf.cell(w=15, h=10, text=f"{idx}.")
        pdf.cell(w=80, h=10, text=p_word)
        pdf.set_draw_color(148, 163, 184)
        pdf.cell(w=75, h=10, border="B", text="", new_x="LMARGIN", new_y="NEXT")
        
    if include_answers:
        pdf.add_page()
        pdf.set_draw_color(16, 185, 129)
        pdf.set_font("helvetica", "B", size=20)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(w=0, h=12, text=f"FACIT: {quiz_title}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(10)
        pdf.set_draw_color(226, 232, 240)
        pdf.set_font("helvetica", "B", size=12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(w=15, h=8, text="Nr", border="B")
        pdf.cell(w=80, h=8, text="Fråga", border="B")
        pdf.cell(w=75, h=8, text="Rätt svar", border="B", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        pdf.set_font("helvetica", size=11)
        for idx, w in enumerate(test_words, 1):
            p_word = w.get("prompt_word", w["svenska"]).replace("➔", "->")
            a_word = w.get("answer_word", w["utlandska"]).replace("➔", "->")
            pdf.set_text_color(51, 65, 85)
            pdf.cell(w=15, h=10, text=f"{idx}.")
            pdf.cell(w=80, h=10, text=p_word)
            pdf.set_text_color(16, 185, 129)
            pdf.cell(w=75, h=10, text=a_word, new_x="LMARGIN", new_y="NEXT")
            
    return pdf.output()

# ================= FUNKTIONER: MOLNDATABAS (GOOGLE SHEETS) =================
@st.cache_data(ttl=15, show_spinner=False)
def fetch_users_from_db(gsheets_url):
    if not gsheets_url: return []
    try:
        payload = {"action": "get_users"}
        req = urllib.request.Request(
            gsheets_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if res_data.get("status") == "success":
                return res_data.get("users", [])
    except Exception:
        pass
    return []

def save_user_progress_to_db(async_save=True):
    if not st.session_state.gsheets_url or not st.session_state.get("logged_in_user"):
        return False
    try:
        payload = {
            "action": "save_progress",
            "name": st.session_state.logged_in_user["name"],
            "leitner": st.session_state.leitner_boxes,
            "score": st.session_state.score,
            "total": st.session_state.total_answered
        }
        if async_save:
            gsheets_url = st.session_state.gsheets_url
            name = st.session_state.logged_in_user["name"]
            leitner = st.session_state.leitner_boxes.copy() if isinstance(st.session_state.leitner_boxes, dict) else {}
            score = st.session_state.score
            total = st.session_state.total_answered

            def worker(url, u_name, u_leitner, u_score, u_total):
                try:
                    payload_async = {"action": "save_progress", "name": u_name, "leitner": u_leitner, "score": u_score, "total": u_total}
                    req_async = urllib.request.Request(url, data=json.dumps(payload_async).encode('utf-8'), headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(req_async, timeout=10): pass
                except: pass

            threading.Thread(target=worker, args=(gsheets_url, name, leitner, score, total), daemon=True).start()
            return True
        else:
            req = urllib.request.Request(st.session_state.gsheets_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data.get("status") == "success"
    except Exception:
        pass
    return False

def create_user_in_db(name, pin, group):
    if not st.session_state.gsheets_url: return False, "Ingen databas ansluten"
    try:
        clean_pin = str(pin).strip().zfill(4) if str(pin).strip().isdigit() else str(pin).strip()
        payload = {"action": "create_user", "name": name.strip(), "pin": clean_pin, "group": group.strip()}
        req = urllib.request.Request(st.session_state.gsheets_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if res_data.get("status") == "success":
                return True, "Elevkonto skapat!"
            else:
                return False, res_data.get("message", "Ett fel uppstod")
    except Exception as e:
        return False, f"Databasfel: {str(e)}"


# ================= STATE MANAGEMENT (INITIERING) =================
if "library" not in st.session_state: st.session_state.library = PERMANENT_LIBRARY.copy()
if "logged_in_user" not in st.session_state: st.session_state.logged_in_user = None
if "selected_category" not in st.session_state: st.session_state.selected_category = None
if "users_list" not in st.session_state: st.session_state.users_list = []
if "last_users_sync" not in st.session_state: st.session_state.last_users_sync = 0
if "words" not in st.session_state:
    first_key = list(st.session_state.library.keys())[0] if st.session_state.library else "Glosor till v. 41"
    st.session_state.words = st.session_state.library[first_key]["words"].copy()
    st.session_state.target_language = "Spanska"
    st.session_state.current_list_name = None

if "direction_mode" not in st.session_state: st.session_state.direction_mode = "Svenska ➔ Målspråk"
if "leitner_boxes" not in st.session_state: st.session_state.leitner_boxes = {}
if "current_streak" not in st.session_state: st.session_state.current_streak = 0
if "show_memory_tip" not in st.session_state: st.session_state.show_memory_tip = False

if st.session_state.gsheets_url and not st.session_state.users_list:
    st.session_state.users_list = fetch_users_from_db(st.session_state.gsheets_url)

def get_word_box(word_sv):
    key = f"{st.session_state.current_list_name}_{word_sv}"
    return st.session_state.leitner_boxes.get(key, 1)

def update_word_box(word_sv, is_correct):
    key = f"{st.session_state.current_list_name}_{word_sv}"
    current_box = st.session_state.leitner_boxes.get(key, 1)
    if is_correct:
        st.session_state.current_streak += 1
        if current_box == 1: st.session_state.leitner_boxes[key] = 2
        elif current_box == 2: st.session_state.leitner_boxes[key] = 3
    else:
        st.session_state.current_streak = 0
        st.session_state.leitner_boxes[key] = 1

curr_words = st.session_state.words if isinstance(st.session_state.get("words"), list) else []
if "shuffled_order" not in st.session_state or len(st.session_state.shuffled_order) != len(curr_words):
    st.session_state.shuffled_order = list(range(len(curr_words))) if curr_words else []
    if st.session_state.shuffled_order: random.shuffle(st.session_state.shuffled_order)

if "current_index" not in st.session_state: st.session_state.current_index = 0
if "score" not in st.session_state: st.session_state.score = 0
if "total_answered" not in st.session_state: st.session_state.total_answered = 0
if "flashcard_flipped" not in st.session_state: st.session_state.flashcard_flipped = False
if "hint_count" not in st.session_state: st.session_state.hint_count = 0
if "quiz_options" not in st.session_state: st.session_state.quiz_options = []
if "quiz_correct_index" not in st.session_state: st.session_state.quiz_correct_index = -1
if "failed_attempts" not in st.session_state: st.session_state.failed_attempts = {}

def reset_progress():
    curr_words = st.session_state.words if isinstance(st.session_state.get("words"), list) else []
    st.session_state.shuffled_order = list(range(len(curr_words))) if curr_words else []
    if st.session_state.shuffled_order: random.shuffle(st.session_state.shuffled_order)
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.total_answered = 0
    st.session_state.current_streak = 0
    st.session_state.show_memory_tip = False
    st.session_state.flashcard_flipped = False
    st.session_state.hint_count = 0
    st.session_state.quiz_options = []
    st.session_state.failed_attempts = {}
    st.session_state.write_correct_answered = False
    st.session_state.write_feedback = None
    if "leitner_boxes" in st.session_state and st.session_state.current_list_name:
        keys_to_remove = [k for k in st.session_state.leitner_boxes if k.startswith(f"{st.session_state.current_list_name}_")]
        for k in keys_to_remove: st.session_state.leitner_boxes[k] = 1

def get_current_word():
    if not st.session_state.get("words"): return None
    curr_words = st.session_state.words
    if "shuffled_order" not in st.session_state or len(st.session_state.shuffled_order) != len(curr_words) or not st.session_state.shuffled_order:
        reset_progress()
    if st.session_state.current_index >= len(curr_words):
        st.session_state.current_index = 0
    idx = st.session_state.shuffled_order[st.session_state.current_index]
    return curr_words[idx] if idx < len(curr_words) else None

def next_word():
    if st.session_state.get("logged_in_user") and st.session_state.logged_in_user["name"] not in ["Gäst", "Lärare"]:
        save_user_progress_to_db(async_save=True)
    if st.session_state.get("words"):
        st.session_state.current_index = (st.session_state.current_index + 1) % len(st.session_state.words)
    else:
        st.session_state.current_index = 0
    st.session_state.flashcard_flipped = False
    st.session_state.hint_count = 0
    st.session_state.quiz_options = []
    st.session_state.write_correct_answered = False
    st.session_state.write_feedback = None
    st.session_state.show_memory_tip = False


# ================= DESIGN & CSS =================
st.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
    <div style="background: linear-gradient(135deg, #3b82f6, #10b981); width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">
        <span style="color: white; font-size: 22px; font-weight: 800; font-family: 'Helvetica Neue', Arial, sans-serif;">G</span>
    </div>
    <div>
        <h1 style="margin: 0; font-size: 34px; font-weight: 800; background: linear-gradient(to right, #1e3a8a, #0d9488); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; letter-spacing: -0.5px;">
            Glos<span style="background: linear-gradient(to right, #0d9488, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Flow</span>
        </h1>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
/* Förenklad och uppfräschad CSS */
button[data-baseweb="tab"] {{
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
    padding: 10px 18px !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.25s ease !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: #1E3A8A !important;
    background-color: #EFF6FF !important;
    border-bottom: 3px solid #3B82F6 !important;
}}

/* List buttons styling */
div[data-testid="element-container"]:has(.folder-card-anchor) + div[data-testid="element-container"] .stButton button,
div[data-testid="element-container"]:has(.list-card-anchor) + div[data-testid="element-container"] .stButton button {{
    border-radius: 10px !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    display: block !important;
    height: auto !important;
}}
div[data-testid="element-container"]:has(.folder-card-anchor) + div[data-testid="element-container"] .stButton button {{
    background-color: #EFF6FF !important; border: 1px solid #3B82F6 !important; border-left: 6px solid #3B82F6 !important;
    padding: 18px 24px !important; font-size: 1.35rem !important; color: #1E3A8A !important; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.05) !important;
}}
div[data-testid="element-container"]:has(.list-card-anchor) + div[data-testid="element-container"] .stButton button {{
    background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
    padding: 16px 20px !important; font-size: 1.2rem !important; color: #1E3A8A !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
}}

@media (prefers-color-scheme: dark) {{
    button[data-baseweb="tab"][aria-selected="true"] {{ color: #60A5FA !important; background-color: #1E293B !important; border-bottom: 3px solid #60A5FA !important; }}
    div[data-testid="element-container"]:has(.folder-card-anchor) + div[data-testid="element-container"] .stButton button {{ background-color: #1E293B !important; border: 1px solid #3B82F6 !important; border-left: 6px solid #3B82F6 !important; color: #60A5FA !important; }}
    div[data-testid="element-container"]:has(.list-card-anchor) + div[data-testid="element-container"] .stButton button {{ background-color: #1E293B !important; border: 1px solid #334155 !important; color: #F8FAFC !important; }}
}}

/* Feedback Animationer */
.quiz-feedback-card {{ padding: 20px !important; border-radius: 12px !important; margin-top: 15px !important; text-align: center !important; font-family: sans-serif !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important; }}
.feedback-correct {{ background: linear-gradient(135deg, #ECFDF5, #D1FAE5) !important; border: 1px solid #A7F3D0 !important; border-left: 6px solid #10B981 !important; color: #065F46 !important; }}
.feedback-incorrect {{ background: linear-gradient(135deg, #FFF5F5, #FEE2E2) !important; border: 1px solid #FCA5A5 !important; border-left: 6px solid #EF4444 !important; color: #991B1B !important; }}
@keyframes pulse-correct {{ 0% {{ box-shadow: 0 0 0 0px rgba(16, 185, 129, 0.3); }} 100% {{ box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }} }}
@keyframes pulse-incorrect {{ 0% {{ box-shadow: 0 0 0 0px rgba(239, 68, 68, 0.3); }} 100% {{ box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }} }}

/* Gamification & Streaks */
.streak-badge {{
    background: linear-gradient(90deg, #f59e0b, #ef4444);
    color: white; padding: 5px 12px; border-radius: 20px;
    font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
}}

/* Kompakt Leitner Horisontell */
.leitner-compact-container {{ display: flex; justify-content: space-between; gap: 10px; margin-bottom: 20px; }}
.leitner-box-stat {{ flex: 1; padding: 12px; border-radius: 8px; text-align: center; background-color: #f8fafc; border: 1px solid #e2e8f0; }}
.l3-stat {{ border-bottom: 4px solid #10b981; }}
.l2-stat {{ border-bottom: 4px solid #f59e0b; }}
.l1-stat {{ border-bottom: 4px solid #ef4444; }}

@media (prefers-color-scheme: dark) {{
    .leitner-box-stat {{ background-color: #1e293b; border-color: #334155; color: #f8fafc; }}
}}
</style>
""", unsafe_allow_html=True)


# ================= INLOGGNING OCH BIBLIOTEK =================
if not st.session_state.logged_in_user:
    st.markdown("<br>", unsafe_allow_html=True)
    col_log_left, col_log_mid, col_log_right = st.columns([1, 4, 1])
    with col_log_mid:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #eff6ff, #ecfdf5); border: 1px solid #bfdbfe; border-left: 6px solid #3b82f6; border-radius: 12px; padding: 25px; text-align: center; margin-bottom: 20px;">
            <h2 style="margin-top: 0; color: #1e3a8a;">Inloggning</h2>
            <p style="color: #475569;">Vänligen logga in med din PIN-kod för att hämta dina framsteg.</p>
        </div>
        """, unsafe_allow_html=True)
        
        login_tab1, login_tab2 = st.tabs(["Elevlogin", "Lärarlogin"])
        
        with login_tab1:
            users = st.session_state.users_list
            groups = sorted(list(set([u["group"] for u in users]))) if users else []
            
            if not users:
                st.warning("Inga elevkonton hittades i databasen än. Din lärare kan logga in i lärarfliken bredvid för att skapa konton.")
                if st.button("Fortsätt som Gäst (Träna offline)", use_container_width=True):
                    st.session_state.logged_in_user = {"name": "Gäst", "group": "Gästklass", "score": 0, "total": 0, "leitner": {}}
                    st.session_state.leitner_boxes = {}
                    st.session_state.current_list_name = None
                    st.rerun()
            else:
                sel_group = st.selectbox("1. Välj din klass:", ["Välj klass..."] + groups)
                if sel_group != "Välj klass...":
                    filtered_users = [u for u in users if u["group"] == sel_group]
                    user_names = sorted([u["name"] for u in filtered_users])
                    sel_name = st.selectbox("2. Välj ditt namn:", ["Välj ditt namn..."] + user_names)
                    if sel_name != "Välj ditt namn...":
                        pin_input = st.text_input("3. Ange din 4-siffriga PIN-kod:", type="password", max_chars=4)
                        if st.button("Logga in ➔", type="primary", use_container_width=True):
                            user = next((u for u in filtered_users if u["name"] == sel_name), None)
                            db_pin = str(user["pin"]).strip() if user else ""
                            in_pin = str(pin_input).strip()
                            if user and (db_pin == in_pin or db_pin.zfill(4) == in_pin.zfill(4)):
                                st.session_state.logged_in_user = user
                                st.session_state.leitner_boxes = user.get("leitner", {})
                                st.session_state.score = user.get("score", 0)
                                st.session_state.total_answered = user.get("total", 0)
                                st.session_state.current_list_name = None
                                st.rerun()
                            else:
                                st.error("Felaktig PIN-kod.")
        with login_tab2:
            entered_admin_pw = st.text_input("Ange administratörslösenord:", type="password")
            if st.button("Logga in som Lärare", type="primary", use_container_width=True):
                if entered_admin_pw == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.session_state.logged_in_user = {"name": "Lärare", "group": "Lärarrummet", "score": 0, "total": 0, "leitner": {}}
                    st.session_state.current_list_name = list(st.session_state.library.keys())[0] if st.session_state.library else None
                    if st.session_state.current_list_name:
                        st.session_state.words = st.session_state.library[st.session_state.current_list_name]["words"].copy()
                        st.session_state.target_language = st.session_state.library[st.session_state.current_list_name]["language"]
                    st.rerun()
                else:
                    st.error("Felaktigt lösenord!")
    st.stop()


# ================= SIDOFÄLT OCH MENY =================
st.sidebar.markdown(f"""
<div style="background: linear-gradient(135deg, #1e3a8a, #0f172a); border-radius: 10px; padding: 12px; color: white; margin-bottom: 15px;">
    <h4 style="margin: 0; color: #10B981; font-size: 1.15rem;">👤 {st.session_state.logged_in_user['name']}</h4>
    <p style="margin: 0; font-size: 0.85rem; color: #94A3B8;">Klass: {st.session_state.logged_in_user['group']}</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.logged_in_user["name"] not in ["Gäst", "Lärare"]:
    if st.sidebar.button("💾 Spara framsteg", use_container_width=True):
        with st.spinner("Sparar..."):
            if save_user_progress_to_db(async_save=False): st.success("Sparat!")
            else: st.error("Kunde inte spara.")

if st.sidebar.button("Logga ut", use_container_width=True):
    if st.session_state.logged_in_user["name"] not in ["Gäst", "Lärare"]:
        save_user_progress_to_db(async_save=False)
    st.session_state.logged_in_user = None
    st.session_state.current_list_name = None
    st.session_state.admin_authenticated = False
    st.rerun()

st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ Träningsinställningar"):
    def sync_direction(): reset_progress()
    st.selectbox(
        "Välj träningsriktning:",
        ("Svenska ➔ Målspråk", "Målspråk ➔ Svenska"),
        key="direction_mode",
        on_change=sync_direction
    )
    if st.button("Nollställ mina framsteg för listan", use_container_width=True):
        reset_progress()
        st.toast("Framsteg nollställda!")


# ================= GLOSBIBLIOTEK =================
if st.session_state.current_list_name is None and st.session_state.logged_in_user["name"] != "Lärare":
    if st.session_state.get("selected_category") is None:
        st.markdown("""<div style="background: linear-gradient(135deg, #1e3a8a, #0d9488); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px;"><h2 style="margin: 0;">📚 Välj kategori</h2></div>""", unsafe_allow_html=True)
        categories_dict = {}
        for name, info in st.session_state.library.items():
            cat = info.get("category", "Övriga listor")
            if cat not in categories_dict: categories_dict[cat] = []
            categories_dict[cat].append(name)
            
        if not categories_dict:
            st.info("Inga gloslistor registrerade än.")
        else:
            for cat_name, list_names in categories_dict.items():
                st.markdown('<div class="folder-card-anchor"></div>', unsafe_allow_html=True)
                if st.button(f"{cat_name}  ({len(list_names)} listor) ➔", key=f"sel_cat_{cat_name}"):
                    st.session_state.selected_category = cat_name
                    st.rerun()
    else:
        cat_name = st.session_state.selected_category
        st.markdown(f"""<div style="background: linear-gradient(135deg, #1e3a8a, #0d9488); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px;"><h2 style="margin: 0;">{cat_name}</h2></div>""", unsafe_allow_html=True)
        if st.button("⬅ Gå tillbaka till mappar", use_container_width=True):
            st.session_state.selected_category = None
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        matching_lists = [name for name, info in st.session_state.library.items() if info.get("category", "Övriga listor") == cat_name]
        for list_name in matching_lists:
            list_info = st.session_state.library[list_name]
            st.markdown('<div class="list-card-anchor"></div>', unsafe_allow_html=True)
            if st.button(f"📄 {list_name}  ({list_info['language']} • {len(list_info['words'])} ord) ➔", key=f"sel_list_{list_name}"):
                st.session_state.current_list_name = list_name
                st.session_state.words = list_info["words"].copy()
                st.session_state.target_language = list_info["language"]
                reset_progress()
                st.rerun()
    st.stop()


# ================= LÄRARPANEL =================
if st.session_state.get("admin_authenticated"):
    teacher_view = st.radio("Välj sidasvy:", ("Lärarpanel", "Elevvy (Övningar)"), horizontal=True)
    if teacher_view == "Lärarpanel":
        st.subheader("Lärarpanel")
        st.info("*(Här kan du bygga vidare på din databas- och list-hantering från originalkoden)*")
        st.stop()


# ================= HUVUDVY: ÖVNING & LEITNER =================
target_lang_name = st.session_state.target_language

# HEADER & NAV
col_back_nav, col_curr_list, col_streak = st.columns([1, 3, 1.5])
with col_back_nav:
    if st.button("📚 Byt Gloslista", use_container_width=True):
        st.session_state.current_list_name = None
        st.session_state.selected_category = None
        st.rerun()
with col_curr_list:
    st.info(f"👉 Aktiv lista: **{st.session_state.current_list_name}**")
with col_streak:
    streak = st.session_state.current_streak
    if streak >= 3:
        st.markdown(f"<div style='text-align:right;'><span class='streak-badge'>🔥 {streak} rätt i rad!</span></div>", unsafe_allow_html=True)
    elif streak > 0:
        st.markdown(f"<div style='text-align:right;'><span style='color:gray; font-weight:bold;'>Streak: {streak}</span></div>", unsafe_allow_html=True)

# NY: CENTRAL LEITNER-ÖVERSIKT (Horisontell)
box1_count = sum(1 for w in (st.session_state.words or []) if get_word_box(w["svenska"]) == 1)
box2_count = sum(1 for w in (st.session_state.words or []) if get_word_box(w["svenska"]) == 2)
box3_count = sum(1 for w in (st.session_state.words or []) if get_word_box(w["svenska"]) == 3)

st.markdown(f"""
<div class="leitner-compact-container">
    <div class="leitner-box-stat l1-stat">🔴 Ska övas: <b>{box1_count}</b></div>
    <div class="leitner-box-stat l2-stat">🟡 På väg: <b>{box2_count}</b></div>
    <div class="leitner-box-stat l3-stat">🟢 Kan bra: <b>{box3_count}</b></div>
</div>
""", unsafe_allow_html=True)


# TABS FÖR ÖVNINGAR
tab1, tab2, tab3 = st.tabs([
    "Flashcards (Rekommenderas för nya ord)",
    "Flervalsquiz (För att testa minnet)",
    "Skrivträning (För att bemästra stavning)"
])

if not st.session_state.words:
    st.warning("⚠️ Ordlistan är tom!")
    st.stop()

current_word = get_current_word()
direction = st.session_state.direction_mode
if direction == "Svenska ➔ Målspråk":
    prompt_lang, target_lang = "svenska", "utlandska"
    label_prompt, label_target = "Svenska", target_lang_name
else:
    prompt_lang, target_lang = "utlandska", "svenska"
    label_prompt, label_target = target_lang_name, "Svenska"


# --- FLIK 1: FLASHCARDS ---
with tab1:
    st.subheader("Träna med digitala ordkort")
    
    # Enklare och snyggare Flashcard med ren HTML/CSS
    card_html = f"""
    <div style="perspective: 1000px; width: 100%; max-width: 400px; margin: 0 auto; height: 220px; cursor: pointer;" onclick="this.classList.toggle('flipped')">
        <div style="position: relative; width: 100%; height: 100%; text-align: center; transition: transform 0.6s; transform-style: preserve-3d;" class="inner-card">
            <style>
                .flipped .inner-card {{ transform: rotateY(180deg); }}
                .face {{ position: absolute; width: 100%; height: 100%; backface-visibility: hidden; border-radius: 12px; border: 2px solid #E2E8F0; display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: #fff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .back {{ transform: rotateY(180deg); }}
                @media (prefers-color-scheme: dark) {{ .face {{ background-color: #1E293B; border-color: #334155; }} }}
            </style>
            <div class="face">
                <h2 style="color: #1E3A8A; font-size: 2rem; margin: 0;">{current_word[prompt_lang]}</h2>
                <p style="color: #64748B; font-size: 0.9rem;">({label_prompt})</p>
                <p style="position:absolute; bottom: 10px; font-size:0.8rem; color: #94A3B8;">Klicka för att vända</p>
            </div>
            <div class="face back">
                <h2 style="color: #10B981; font-size: 2rem; margin: 0;">{current_word[target_lang]}</h2>
                <p style="color: #64748B; font-size: 0.9rem;">({label_target})</p>
            </div>
        </div>
    </div>
    """
    components.html(card_html, height=250)
    
    if st.button("Nästa kort ➔", use_container_width=True):
        if st.session_state.get("logged_in_user") and st.session_state.logged_in_user["name"] not in ["Gäst", "Lärare"]:
            st.session_state.leitner_boxes["_stats_flashcard_total"] = st.session_state.leitner_boxes.get("_stats_flashcard_total", 0) + 1
        next_word()
        st.rerun()

# --- FLIK 2: QUIZ ---
with tab2:
    st.subheader("Flervalsquiz")
    
    # Knappen för proaktiva hints
    if st.button("🧠 Visa minnesknep", key="hint_btn_quiz"):
        st.session_state.show_memory_tip = True
        
    if st.session_state.show_memory_tip:
        st.info(get_strategy_tip(current_word, target_lang_name))
        
    if not st.session_state.quiz_options or len(st.session_state.quiz_options) < 4:
        correct_ans = current_word[target_lang]
        other_words = [w[target_lang] for w in st.session_state.words if w[target_lang] != correct_ans]
        distractors = random.sample(other_words, 3) if len(other_words) >= 3 else other_words + ["time", "year", "way"][:3 - len(other_words)]
        options = distractors + [correct_ans]
        random.shuffle(options)
        st.session_state.quiz_options = options
        st.session_state.quiz_answered_option = None
        st.session_state.quiz_scored = False

    st.markdown(f"Vad betyder: **{current_word[prompt_lang]}**?")
    correct_ans = current_word[target_lang]
    
    if st.session_state.quiz_answered_option is None:
        selected = st.radio("Svar:", st.session_state.quiz_options, index=None, label_visibility="collapsed", key="q_radio_active")
        if selected:
            st.session_state.quiz_answered_option = selected
            st.rerun()
    else:
        selected = st.session_state.quiz_answered_option
        st.radio("Svar:", st.session_state.quiz_options, index=st.session_state.quiz_options.index(selected), disabled=True, label_visibility="collapsed", key="q_radio_disabled")
        
        if not st.session_state.quiz_scored:
            st.session_state.total_answered += 1
            is_correct = (selected == correct_ans)
            if is_correct: st.session_state.score += 1
            update_word_box(current_word["svenska"], is_correct)
            st.session_state.quiz_scored = True
            
        if selected == correct_ans:
            st.markdown(f"""<div class="quiz-feedback-card feedback-correct" style="animation: pulse-correct 1s infinite alternate;"><h3>🎉 Rätt svar!</h3><p><b>{current_word[prompt_lang]}</b> är <b>{correct_ans}</b>.</p></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="quiz-feedback-card feedback-incorrect" style="animation: pulse-incorrect 1s infinite alternate;"><h3>❌ Tyvärr fel</h3><p>Rätt svar är: <b>{correct_ans}</b></p></div>""", unsafe_allow_html=True)

        if st.button("Nästa fråga ➔", use_container_width=True, type="primary"):
            next_word()
            st.rerun()

# --- FLIK 3: SKRIVTRÄNING ---
with tab3:
    st.subheader("Aktiv återkallning")
    st.markdown(f"Översätt ordet: <h3 style='display:inline;'>{current_word[prompt_lang]}</h3>", unsafe_allow_html=True)
    
    col_w_hint1, col_w_hint2 = st.columns(2)
    with col_w_hint1:
        if st.button("🧠 Visa minnesknep", key="hint_btn_write"):
            st.session_state.show_memory_tip = True
    
    if st.session_state.show_memory_tip:
        st.info(get_strategy_tip(current_word, target_lang_name))

    button_label = "Nästa ord ➔ [Tryck på Enter]" if st.session_state.write_correct_answered else "Rätta mitt svar [Enter]"

    with st.form("write_form"):
        user_input = st.text_input("Skriv din översättning här:", key="write_input", placeholder="Stava noggrant...")
        col1, col2 = st.columns(2)
        with col1:
            check_write = st.form_submit_button(button_label, use_container_width=True, type="primary" if st.session_state.write_correct_answered else "secondary")
        with col2:
            hint_btn = st.form_submit_button("💡 Få en bokstav", use_container_width=True, disabled=st.session_state.write_correct_answered)
            
    components.html("""<script>setTimeout(function() {var inputs = window.parent.document.querySelectorAll('div[data-testid="stTextInput"] input'); if (inputs.length > 0) inputs[inputs.length - 1].focus(); }, 100);</script>""", height=0, width=0)
            
    target_word = current_word[target_lang]
    if hint_btn:
        if st.session_state.hint_count < len(target_word): st.session_state.hint_count += 1
        st.rerun()
        
    if st.session_state.hint_count > 0:
        hint_text = target_word[:st.session_state.hint_count] + "_" * (len(target_word) - st.session_state.hint_count)
        st.info(f"Bokstavsledtråd: `{hint_text}`")
        
    if check_write:
        if st.session_state.write_correct_answered:
            next_word()
            st.rerun()
        elif not user_input.strip():
            st.warning("Skriv in ett svar först!")
        else:
            st.session_state.total_answered += 1
            clean_correct = target_word.strip().lower().rstrip('. ')
            clean_student = user_input.strip().lower().rstrip('. ')
            
            is_correct = (clean_student == clean_correct)
            update_word_box(current_word["svenska"], is_correct)
            
            if is_correct:
                st.session_state.score += 1
                st.session_state.write_correct_answered = True
                st.session_state.write_feedback = {"type": "success", "text": f"🎉 Strålande! **{current_word[prompt_lang]}** stavas mycket riktigt **{target_word}**."}
            else:
                st.session_state.write_correct_answered = False
                st.session_state.write_feedback = {"type": "error", "text": f"❌ Felstavat eller fel ord. Det korrekta svaret är **{target_word}**."}
            st.rerun()

    if st.session_state.get("write_feedback"):
        if st.session_state.write_feedback["type"] == "success":
            st.success(st.session_state.write_feedback["text"])
            st.info("👉 Tryck på **Enter** igen eller klicka på knappen ovan för att gå vidare!")
        else:
            st.error(st.session_state.write_feedback["text"])
