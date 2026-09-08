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

def clean_html(html_str):
    return "\n".join(line.strip() for line in html_str.split("\n"))



# Spårning och förslag på inlärningsstrategier enligt vetenskapliga principer (Mnemonic & Dual Coding)
def get_strategy_tip(word_obj, language):
    sv = word_obj["svenska"].lower().strip()
    ut = word_obj["utlandska"].lower().strip()
    
    # Custom spanska nyckelordstips (Mnemonic Keyword Technique)
    spanish_tips = {
        "ser": "**Associationstips:** *ser* är grundformen för att vara på spanska. Tänk på ordet *seriös* eller engelskans *series* (en serie av händelser som bara 'är').",
        "suecia": "**Kognat-tips:** *Suecia* låter nästan som *Sverige* på franska (*Suède*) eller engelska (*Sweden*)!",
        "español": "**Kognat-tips:** *español* är väldigt likt svenskans spanska och engelskans *Spanish*.",
        "inglés": "**Kognat-tips:** *inglés* är superlikt *engelska* (eller franskans *anglais*).",
        "hablo": "**Associationstips:** *hablo* kommer från *hablar* (att prata). Tänk på 'hävla ur sig' ord eller engelskans *babble* (babbit/prata).",
        "lunes": "**Etymologitips:** *lunes* kommer från latinets *luna* (måne) [30]. Måndag är helt enkelt 'måndagen'!",
        "martes": "**Etymologitips:** *martes* är uppkallat efter krigsguden Mars [30]. På svenska är tisdag uppkallad efter vår krigsgud Tyr – båda dagarna tillhör krigsgudarna!",
        "miércoles": "**Etymologitips:** *miércoles* är uppkallat efter budbäraren och handelsguden Merkurius [30].",
        "jueves": "**Etymologitips:** *jueves* är uppkallat efter dunder- och blixtguden Jupiter [30]. På svenska är torsdag Tors dag (vår egen dunder- och blixtgud) – en klockren koppling!",
        "viernes": "**Etymologitips:** *viernes* är uppkallat efter kärleksgudinnan Venus [30]. På svenska är fredag Frejas dag (vår kärleksgudinna) – båda hyllar kärleken!",
        "sábado": "**Associationstips:** *sábado* är nära besläktat med ordet *sabbat* (vilodag) [30]. Det är lördag och dags för vila!",
        "domingo": "**Associationstips:** *domingo* kommer från latinets *dominus* (herre) och betyder 'herrens dag' [30]. Tänk på ordet *dominera* – herren dominerar på söndagar!",

        "bok": "**Nyckelordstips:** *libro* låter lite som engelskans *library* (bibliotek) eller spanskans *libre* (fri) [30, 1104]. Föreställ dig en fri bok som flyger ut genom klassrumsfönstret! [247]",
        "blyertspenna": "**Nyckelordstips:** *lápiz* låter som *lapis* (blå sten) eller som att 'lappa' [15]. Föreställ dig att du ritar röda lappar på din skoldator med en gigantisk blyertspenna! [247]",
        "bläckpenna": "**Orddelstips:** *bolígrafo* slutar på *-grafo* (skriva), precis som geografi, biografi eller grafit [724]. Det hat alltid med skrivande att göra! [27]",
        "skrivhäfte": "**Nyckelordstips:** *cuaderno* låter lite som *kvadrat* (*cuadrado* på spanska). Föreställ dig ett helt fyrkantigt, kvadratiskt skrivhäfte! [247]",
        "ett papper (pappersark)": "**Associationstips:** *hoja de papel* – *papel* känner du igen, och *hoja* betyder egentligen blad (som på ett träd). Ett papper är helt enkelt ett pappersblad!",
        "ryggsäck": "**Nyckelordstips:** *mochila* låter som *mojito* eller att *mucka*. Föreställ dig en hel mojito (läsk) som läcker i din ryggsäck! [247]",
        "skåp": "**Associationstips:** *casilla* låter som *casa* (hus) eller *kasse*. Föreställ dig en kasse som du låser in i ditt skolkåp!",
        "dator": "**Kognat-tips:** *computadora* är nästan identiskt med engelskans *computer* [30, 957]. Enkel kognat! *Ordenador* låter som att 'ordna' – datorn ordnar dina filer.",
        "laddare": "**Kognat-tips:** *cargador* hänger ihop med engelskans *charge* (ladda) [1]. En *cargador* är det du laddar med!",
        "sudd": "**Kognat-tips:** *goma* låter som *gummi* (suddgummi) [1, 919]. Tänk dig ett suddgummi av tuggummi!",
        "surfplatta": "**Kognat-tips:** *tableta* låter som *tablett* (en liten platta eller medicin) [30]. Superlätt kognat!",
        "tavla": "**Nyckelordstips:** *pizarra* låter lite som *pizzor*. Föreställ dig att klassrummets tavla är gjord av en gigantisk, rund pizza! [247]",
        "god morgon/god dag": "**Orddelstips:** *buenos días* – *buenos* betyder bra, och *días* betyder dagar. 'Bra dagar' = god dag!",
        "hej då, farväl": "**Associationstips:** *adiós* kommer historiskt från 'A Dios' (till Gud) – en klassisk hälsning när man går.",
        "jag är här": "**Nyckelordstips:** *estoy aquí* – *estoy* betyder 'jag är' och *aquí* betyder 'här'. Tänk på akvarium – 'jag är här i akvariet!'",
        "elever": "**Associationstips:** *alumnos* låter som *alumni* (tidigare elever) eller ordet *alumn*. Det betyder helt enkelt elever!",
        "hund": "**Nyckelordstips:** *perro* låter lite som *pärla*. Föreställ dig en fluffig hund som bär ett glittrande pärlhalsband! [249, 1235]",
        "katt": "**Kognat-tips:** *gato* är besläktat med engelskans *cat* och tyskans *Katze* [30]. Tänk dig en katt i en hög svart hatt!",
        "äpple": "**Nyckelordstips:** *manzana* låter lite som *manschett*. Föreställ dig ett rött äpple som har små fina skjortmanschetter runt stjälken! [247]",
        "vän": "**Associationstips:** *amigo* känner du säkert igen! Det hänger ihop med amor (kärlek) och spanskans ord för vänskap. En riktig kompis!",
        "hus": "**Associationstips:** *casa* – tänk på *casablanca* (vitt hus) eller *husbil* (*caravan*). *Casa* = hus!",
        "hus": "**Associationstips:** *casa* – tänk på *casablanca* (vitt hus) eller *husbil* (*caravan*). *Casa* = hus!",
        "tid": "**Kognat-tips:** *tiempo* låter som engelskans *tempo* eller *time*. Tempo handlar om tid!",
        "det är...": "**Associationstips:** *hace...* kommer från verbet *hacer* (att göra). På spanska \'gör\' man väder, t.ex. \'det gör sol\' eller \'det gör kallt\'!",
        "det blåser": "**Nyckelordstips:** *hace viento* – *viento* låter som svenskans *vind* eller engelskans *wind*. Det blåser hård vind!",
        "det är kallt": "**Associationstips:** *hace frío* – *frío* är jättenära svenskans *frysa* och engelskans *freezing*! Lätt att koppla till kyla.",
        "det är varmt": "**Nyckelordstips:** *hace calor* – *calor* låter som *kalorier* (som ger värme!) eller engelskans *calories*.",
        "det är dåligt väder": "**Associationstips:** *hace mal tiempo* – *mal* betyder dåligt (tänk på *malplacerad* eller *malström*) och *tiempo* betyder väder/tid. Det är helt enkelt \'dålig tid\'!",
        "det är bra väder": "**Associationstips:** *hace buen tiempo* – *buen* känner du igen från *buenos días* (bra dagar) och *tiempo* är tid/väder. \'Bra tid\'!",
        "det är soligt": "**Kognat-tips:** *hace sol* – *sol* stavas och betyder exakt samma sak på spanska som på svenska! Superlätt kognat.",
        "det är molnigt": "**Nyckelordstips:** *está nublado* – *nublado* låter lite som *nebulosa* (ett moln av gas i rymden) eller *nimbusmoln*. Tänk dig ett stort, grått nimbusmoln!",
        "det regnar": "**Associationstips:** *llueve* kommer från verbet *llover*. Tänk på engelskans *deluge* (syndaflod/störtregn) eller spanskans *lluvia* (regn). Dubbel-L uttalas som j-ljud!",
        "det snöar": "**Kognat-tips:** *nieva* kommer från *nevar*. Det är släkt med ord som *neve* (snö på italienska/latin) eller *niveus* (snövit). Tänk på det snötäckta berget *Sierra Nevada* (Snöklädda bergskedjan)!",
        "vinter": "**Kognat-tips:** *invierno* är släkt med engelskans *hibernate* (att övervintra) och franskans *hiver*. Tänk på björnen som går i ide under vintern!",
        "sommar": "**Associationstips:** *verano* låter lite som *veranda*. Föreställ dig att du sitter på en solig veranda mitt i varma sommaren!",
        "vår": "**Kognat-tips:** *primavera* – *prima* betyder första (som primör) och *vera* kommer från ett gammalt ord för vår. Våren är årets \'första grönska\'!",
        "höst": "**Nyckelordstips:** *otoño* låter lite som engelskans *autumn*. Samma startbokstav och väldigt lik känsla!",
        "årstid": "**Kognat-tips:** *estación* är väldigt likt engelskans *station* eller *season* (via franskans säsong). Tänk på årets fyra stationer som tåget stannar vid!",
        "vad är det för väder?": "**Associationstips:** *¿qué tiempo hace?* betyder ordagrant \'vilket väder gör det?\' eftersom *tiempo* betyder både tid och väder, och *hace* betyder \'gör\'!" 
    }
    
    # Custom engelska nyckelordstips (Top 50)
    english_tips = {
        "tid": "**Kognat-tips:** *time* stavas nästan som tid och uttalas nästan likadant! [30]",
        "år": "**Associationstips:** *year* – tänk på nyår (*New Year*) eller födelsedag (*birthday*).",
        "folk": "**Associationstips:** *people* – tänk på 'pöbel' eller engelskans populära *people*.",
        "sätt": "**Associationstips:** *way* – tänk på *highway* (motorväg) eller 'on my way' (på min väg/mitt sätt).",
        "dag": "**Kognat-tips:** *day* är en enkel kognat. Det låter nästan som det svenska ordet dag! [30]",
        "sak": "**Associationstips:** *thing* – tänk på 'ingenting' (*nothing*) eller 'någonting' (*something*) – *thing* är en sak!",
        "man": "**Kognat-tips:** *man* stavas och betyder exakt samma sak på engelska! [30]",
        "värld": "**Associationstips:** *world* – tänk på världskarta (*World Map*) eller *World Wide Web* (www).",
        "liv": "**Associationstips:** *life* – tänk på livvakt (*lifeguard*) eller livsstil (*lifestyle*).",
        "skola": "**Kognat-tips:** *school* är mycket likt svenska skola! Enkel kognat [30].",
        "familj": "**Kognat-tips:** *family* är mycket likt svenskans familj. Enkel kognat [30].",
        "student": "**Kognat-tips:** *student* stavas och betyder exakt samma sak på engelska! [30]",
        "land": "**Associationstips:** *country* – tänk på countrymusik (landsbygdsmusik) eller *countryside*.",
        "problem": "**Kognat-tips:** *problem* stavas och betyder exakt samma sak på engelska! [30]",
        "hand": "**Kognat-tips:** *hand* stavas och betyder exakt samma sak på engelska! [30]",
        "del": "**Associationstips:** *part* – tänk på partner eller att ta del av en 'part' (en bit).",
        "plats": "**Kognat-tips:** *place* är mycket likt svenskans 'plats'. Tänk på marknadsplats (*marketplace*) [30].",
        "vecka": "**Associationstips:** *week* – tänk på helg (*weekend*) eller veckodag (*weekday*).",
        "arbete": "**Associationstips:** *work* – mycket likt svenskans verk/verksamhet. *Work* = arbete!",
        "system": "**Kognat-tips:** *system* stavas och betyder exakt samma sak på engelska! [30]"
    }
    
    if language.lower() == "spanska" and sv in spanish_tips:
        return spanish_tips[sv]
    elif language.lower() == "engelska" and sv in english_tips:
        return english_tips[sv]
    
    return f"**Nyckelordsmetoden:** Prova att hitta ett svenskt ord som låter som det utländska ordet '{ut}'. Föreställ dig sedan en rolig eller konstig bild i huvudet där det ordet kopplas ihop med betydelsen '{sv}'! Det hjälper hjärnan att bygga en stark form-betydelse-bro [31, 247]."


def generate_pdf_bytes(test_words, quiz_title, target_lang_name, include_answers):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margin(20)
    
    # Accent color (#10B981)
    pdf.set_draw_color(16, 185, 129)
    
    # Title
    pdf.set_font("helvetica", "B", size=20)
    pdf.set_text_color(30, 58, 138) # Dark Blue
    pdf.cell(w=0, h=12, text=quiz_title, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Divider line
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(8)
    
    # Student Info box
    pdf.set_text_color(51, 65, 85) # Slate Dark Gray
    pdf.set_font("helvetica", size=11)
    pdf.cell(w=30, h=8, text="Elevens namn:")
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
    
    # Table headers
    pdf.set_draw_color(226, 232, 240) # Light slate grey
    pdf.set_font("helvetica", "B", size=12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w=15, h=8, text="Nr", border="B")
    pdf.cell(w=80, h=8, text="Svenska / Glosa", border="B")
    pdf.cell(w=75, h=8, text="Översättning", border="B", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    # Rows
    pdf.set_font("helvetica", size=11)
    pdf.set_text_color(51, 65, 85)
    for idx, w in enumerate(test_words, 1):
        p_word = w.get("prompt_word", w["svenska"]).replace("➔", "->")
        pdf.cell(w=15, h=10, text=f"{idx}.")
        pdf.cell(w=80, h=10, text=p_word)
        pdf.set_draw_color(148, 163, 184) # slate-400
        pdf.cell(w=75, h=10, border="B", text="", new_x="LMARGIN", new_y="NEXT")
        
    # Page 2: Facit
    if include_answers:
        pdf.add_page()
        pdf.set_draw_color(16, 185, 129)
        pdf.set_font("helvetica", "B", size=20)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(w=0, h=12, text=f"FACIT: {quiz_title}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(10)
        
        # Table headers
        pdf.set_draw_color(226, 232, 240)
        pdf.set_font("helvetica", "B", size=12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(w=15, h=8, text="Nr", border="B")
        pdf.cell(w=80, h=8, text="Fråga", border="B")
        pdf.cell(w=75, h=8, text="Rätt svar", border="B", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        
        # Rows
        pdf.set_font("helvetica", size=11)
        for idx, w in enumerate(test_words, 1):
            p_word = w.get("prompt_word", w["svenska"]).replace("➔", "->")
            a_word = w.get("answer_word", w["utlandska"]).replace("➔", "->")
            pdf.set_text_color(51, 65, 85)
            pdf.cell(w=15, h=10, text=f"{idx}.")
            pdf.cell(w=80, h=10, text=p_word)
            pdf.set_text_color(16, 185, 129) # Emerald Green
            pdf.cell(w=75, h=10, text=a_word, new_x="LMARGIN", new_y="NEXT")
            
    return pdf.output()


# ================= MOLNDATABAS (GOOGLE SHEETS) HJÄLPFUNKTIONER =================
@st.cache_data(ttl=15, show_spinner=False)
def fetch_users_from_db(gsheets_url):
    if not gsheets_url:
        return []
    try:
        payload = {"action": "get_users"}
        req = urllib.request.Request(
            gsheets_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            res_data = json.loads(res_body)
            if res_data.get("status") == "success":
                return res_data.get("users", [])
    except Exception as e:
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
            # Copy leitner boxes to avoid thread race conditions
            leitner = st.session_state.leitner_boxes.copy() if isinstance(st.session_state.leitner_boxes, dict) else {}
            score = st.session_state.score
            total = st.session_state.total_answered

            def worker(url, u_name, u_leitner, u_score, u_total):
                try:
                    payload_async = {
                        "action": "save_progress",
                        "name": u_name,
                        "leitner": u_leitner,
                        "score": u_score,
                        "total": u_total
                    }
                    req_async = urllib.request.Request(
                        url,
                        data=json.dumps(payload_async).encode('utf-8'),
                        headers={'Content-Type': 'application/json'}
                    )
                    with urllib.request.urlopen(req_async, timeout=10) as response:
                        pass
                except:
                    pass

            threading.Thread(target=worker, args=(gsheets_url, name, leitner, score, total), daemon=True).start()
            return True
        else:
            req = urllib.request.Request(
                st.session_state.gsheets_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode('utf-8')
                res_data = json.loads(res_body)
                return res_data.get("status") == "success"
    except Exception as e:
        pass
    return False

def create_user_in_db(name, pin, group):
    if not st.session_state.gsheets_url:
        return False, "Ingen databas ansluten"
    try:
        payload = {
            "action": "create_user",
            "name": name.strip(),
            "pin": str(pin).strip(),
            "group": group.strip()
        }
        req = urllib.request.Request(
            st.session_state.gsheets_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            res_data = json.loads(res_body)
            if res_data.get("status") == "success":
                return True, "Elevkonto skapat!"
            else:
                return False, res_data.get("message", "Ett fel uppstod")
    except Exception as e:
        return False, f"Databasfel: {str(e)}"

# Sätt sidkonfiguration
st.set_page_config(
    page_title="GlosFlow - Digitala Glostränaren",
    page_icon="G",
    layout="centered"
)

# --- LÄRARKONFIGURATION (VALFRITT) ---
ADMIN_PASSWORD = "skola123"

# Du kan förbereda permanenta listor i biblioteket direkt i koden här!
# Detta gör att de alltid ligger laddade för eleverna när hemsidan startas.
PERMANENT_LIBRARY = {
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
    },
    "Spanska - veckodagar": {
        "language": "Spanska",
        "category": "Tematiska ordlistor",
        "words": [
            {"svenska": "måndag", "utlandska": "lunes"},
            {"svenska": "tisdag", "utlandska": "martes"},
            {"svenska": "onsdag", "utlandska": "miércoles"},
            {"svenska": "torsdag", "utlandska": "jueves"},
            {"svenska": "fredag", "utlandska": "viernes"},
            {"svenska": "lördag", "utlandska": "sábado"},
            {"svenska": "söndag", "utlandska": "domingo"}
        ]
    }
}

# Initiera biblioteket i session state
if "library" not in st.session_state:
    st.session_state.library = PERMANENT_LIBRARY.copy()

# Inloggnings- och elevstatus
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "users_list" not in st.session_state:
    st.session_state.users_list = []
if "last_users_sync" not in st.session_state:
    st.session_state.last_users_sync = 0

if "gsheets_url" not in st.session_state:
    st.session_state.gsheets_url = st.secrets.get("GSHEETS_URL", "https://script.google.com/macros/s/AKfycbx-CeGayXVPneyqfB-CNUzb4lrM-QejzQO96oJrjN0gMpUc1xDcVft_xbvrS8v6r9MC0w/exec")

# Hämta användare från molndatabasen vid uppstart
if st.session_state.gsheets_url and not st.session_state.users_list:
    st.session_state.users_list = fetch_users_from_db(st.session_state.gsheets_url)


# Initiera aktiv ordlista och målspråk
if "words" not in st.session_state:
    st.session_state.words = st.session_state.library["Spanska nybörjare - till v. 37"]["words"].copy()
    st.session_state.target_language = "Spanska"
    st.session_state.current_list_name = None

if "current_list_name" not in st.session_state:
    st.session_state.current_list_name = None

if "direction_mode" not in st.session_state:
    st.session_state.direction_mode = "Svenska ➔ Målspråk"

if "mn_direction" not in st.session_state:
    st.session_state.mn_direction = st.session_state.direction_mode

if "sb_direction" not in st.session_state:
    st.session_state.sb_direction = st.session_state.direction_mode

if "target_language" not in st.session_state:
    st.session_state.target_language = "Spanska"

# Initiera spelmekanik

if "leitner_boxes" not in st.session_state:
    st.session_state.leitner_boxes = {}

# Helper-funktioner för Leitner-lådssystemet
def get_word_box(word_sv):
    if "leitner_boxes" not in st.session_state:
        st.session_state.leitner_boxes = {}
    key = f"{st.session_state.current_list_name}_{word_sv}"
    return st.session_state.leitner_boxes.get(key, 1)

def update_word_box(word_sv, is_correct):
    if "leitner_boxes" not in st.session_state:
        st.session_state.leitner_boxes = {}
    key = f"{st.session_state.current_list_name}_{word_sv}"
    current_box = st.session_state.leitner_boxes.get(key, 1)
    if is_correct:
        if current_box == 1:
            st.session_state.leitner_boxes[key] = 2
        elif current_box == 2:
            st.session_state.leitner_boxes[key] = 3
    else:
        # Vid fel faller ordet tillbaka till Låda 1 för mer intensiv träning (klassiskt Leitner-system)
        st.session_state.leitner_boxes[key] = 1

if "shuffled_order" not in st.session_state or len(st.session_state.shuffled_order) != len(st.session_state.words):
    st.session_state.shuffled_order = list(range(len(st.session_state.words)))
    random.shuffle(st.session_state.shuffled_order)

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "total_answered" not in st.session_state:
    st.session_state.total_answered = 0

if "flashcard_flipped" not in st.session_state:
    st.session_state.flashcard_flipped = False

if "hint_count" not in st.session_state:
    st.session_state.hint_count = 0

if "quiz_options" not in st.session_state:
    st.session_state.quiz_options = []

if "quiz_correct_index" not in st.session_state:
    st.session_state.quiz_correct_index = -1

# Spåra felaktiga försök per ord för att erbjuda strategier
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = {}

# Funktion för att nollställa framsteg och blanda om ordningen
def reset_progress():
    st.session_state.shuffled_order = list(range(len(st.session_state.words)))
    random.shuffle(st.session_state.shuffled_order)
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.total_answered = 0
    st.session_state.flashcard_flipped = False
    st.session_state.hint_count = 0
    st.session_state.quiz_options = []
    st.session_state.failed_attempts = {}
    st.session_state.write_correct_answered = False
    st.session_state.write_feedback = None
    
    # Återställ Leitner-lådor för den aktiva listan till Låda 1
    if "leitner_boxes" in st.session_state:
        keys_to_remove = [k for k in st.session_state.leitner_boxes if k.startswith(f"{st.session_state.current_list_name}_")]
        for k in keys_to_remove:
            st.session_state.leitner_boxes[k] = 1

# Funktion för att hämta nuvarande ord baserat på den blandade listan
def get_current_word():
    if not st.session_state.words:
        return None
    idx = st.session_state.shuffled_order[st.session_state.current_index]
    if idx >= len(st.session_state.words):
        reset_progress()
        idx = st.session_state.shuffled_order[st.session_state.current_index]
    return st.session_state.words[idx]

# Gå till nästa ord
def next_word():
    # Autospara elevens framsteg i bakgrunden vid byte av ord
    if st.session_state.get("logged_in_user") and st.session_state.logged_in_user["name"] not in ["Gäst", "Lärare"]:
        save_user_progress_to_db(async_save=True)
    st.session_state.current_index = (st.session_state.current_index + 1) % len(st.session_state.words)
    st.session_state.flashcard_flipped = False
    st.session_state.hint_count = 0
    st.session_state.quiz_options = []
    st.session_state.write_correct_answered = False
    st.session_state.write_feedback = None

# --- APP DESIGN & GRÄNSSNITT ---
# Custom elegant branding logo for GlosFlow with CSS
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

st.markdown("""
<div class="welcome-banner-card">
    <p class="welcome-banner-text">
        Välkommen till <b>GlosFlow</b>! Öva i din egen takt med vetenskapligt beprövade metoder för språkinlärning.
    </p>
</div>
""", unsafe_allow_html=True)






# ================= ELEVINLOGGNING & GLOSBIBLIOTEK-SKÄRM =================
# Kontrollera om användaren är inloggad. Om inte, visa den vackra login-skärmen.
if not st.session_state.logged_in_user:
    st.markdown("<br>", unsafe_allow_html=True)
    col_log_left, col_log_mid, col_log_right = st.columns([1, 4, 1])
    with col_log_mid:
        st.markdown("""
        <div class="login-banner-card">
            <h2 class="login-banner-title">Inloggning</h2>
            <p class="login-banner-text">Vänligen logga in med din PIN-kod som du fått av din lärare för att hämta dina framsteg.</p>
        </div>
        """, unsafe_allow_html=True)
        
        login_tab1, login_tab2 = st.tabs(["Elevlogin", "Lärarlogin"])
        
        with login_tab1:
            users = st.session_state.users_list
            groups = sorted(list(set([u["group"] for u in users]))) if users else []
            
            if not users:
                st.warning("Inga elevkonton hittades i databasen än. Din lärare kan logga in i lärarfliken bredvid för att skapa konton och ansluta kalkylarket.")
                if st.button("Fortsätt som Gäst (Träna offline)", use_container_width=True):
                    st.session_state.logged_in_user = {"name": "Gäst", "group": "Gästklass", "score": 0, "total": 0, "leitner": {}}
                    st.session_state.leitner_boxes = {}
                    st.session_state.current_list_name = None
                    st.toast("Inloggad som gäst!")
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
                            # Hitta elev
                            user = next((u for u in filtered_users if u["name"] == sel_name), None)
                            if user and str(user["pin"]).strip() == str(pin_input).strip():
                                st.session_state.logged_in_user = user
                                st.session_state.leitner_boxes = user.get("leitner", {})
                                st.session_state.score = user.get("score", 0)
                                st.session_state.total_answered = user.get("total", 0)
                                st.session_state.current_list_name = None # Starta med listväljaren!
                                st.toast(f"Välkommen tillbaka, {sel_name}! Din progression är laddad.")
                                st.rerun()
                            else:
                                st.error("Felaktig PIN-kod. Försök igen eller fråga din lärare.")
            
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
                    st.toast("Lärarläge upplåst!")
                    st.rerun()
                else:
                    st.error("Felaktigt lösenord!")
    st.stop()

# --- SIDOMENY: PROFIL & LEITNER-STADA ---
st.sidebar.markdown(f"""
<div style="background: linear-gradient(135deg, #1e3a8a, #0f172a); border-radius: 10px; padding: 12px; color: white; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(30, 58, 138, 0.15);">
    <h4 style="margin: 0; color: #10B981; font-size: 1.15rem;">👤 {st.session_state.logged_in_user['name']}</h4>
    <p style="margin: 0; font-size: 0.85rem; color: #94A3B8;">Klass: {st.session_state.logged_in_user['group']}</p>
</div>
""", unsafe_allow_html=True)

# Knapp för att spara framsteg manuellt
if st.session_state.logged_in_user["name"] != "Gäst" and st.session_state.logged_in_user["name"] != "Lärare":
    col_save, col_logout = st.columns(2)
    with col_save:
        if st.button("💾 Spara", use_container_width=True, help="Spara dina framsteg i molnet"):
            with st.spinner("Sparar..."):
                success = save_user_progress_to_db(async_save=False)
                if success:
                    st.toast("Framsteg sparade!")
                    st.success("Sparat!")
                else:
                    st.error("Kunde inte spara.")
    with col_logout:
        if st.button("Logga ut", use_container_width=True):
            with st.spinner("Sparar framsteg..."):
                save_user_progress_to_db(async_save=False)
            st.session_state.logged_in_user = None
            st.session_state.current_list_name = None
            st.session_state.words = None
            st.toast("Utloggad!")
            st.rerun()
else:
    if st.sidebar.button("Logga ut", use_container_width=True):
        st.session_state.logged_in_user = None
        st.session_state.current_list_name = None
        st.session_state.words = None
        st.session_state.admin_authenticated = False
        st.toast("Utloggad!")
        st.rerun()

# Färgtema inställningar
st.sidebar.markdown("---")
st.sidebar.subheader("Färgtema")
theme_mode = st.sidebar.selectbox(
    "Välj färgtema:",
    ("Följ systemet", "Ljust läge", "Mörkt läge"),
    key="theme_mode",
    help="Här kan du byta färgtema för appen. 'Följ systemet' anpassar sig automatiskt efter din enhets ljusa eller mörka läge."
)

# Konstruera CSS baserat på valt färgtema
theme_css = ""
flashcard_theme_css = ""

if theme_mode == "Mörkt läge 🌙":
    theme_css = """
    .box-l1 {
        background-color: #451a1a !important;
        border: 2px solid #7f1d1d !important;
    }
    .box-l1 h4 {
        color: #fca5a5 !important;
    }
    .box-l1 h4 small {
        color: #ef4444 !important;
    }
    .box-l2 {
        background-color: #45290a !important;
        border: 2px solid #78350f !important;
    }
    .box-l2 h4 {
        color: #fcd34d !important;
    }
    .box-l2 h4 small {
        color: #f59e0b !important;
    }
    .box-l3 {
        background-color: #064e3b !important;
        border: 2px solid #065f46 !important;
    }
    .box-l3 h4 {
        color: #a7f3d0 !important;
    }
    .box-l3 h4 small {
        color: #10b981 !important;
    }
    .leitner-card {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border-left-width: 4px !important;
    }
    """
    flashcard_theme_css = """
    .flashcard-front, .flashcard-back {
        background-color: #1E293B !important;
        border-color: #334155 !important;
    }
    .card-word {
        color: #60A5FA !important;
    }
    .card-word-back {
        color: #34D399 !important;
    }
    .card-lang {
        color: #94A3B8 !important;
    }
    .card-hint-text {
        color: #64748B !important;
    }
    """
elif theme_mode == "Ljust läge ☀️":
    theme_css = """
    .box-l1 {
        background-color: #FEE2E2 !important;
        border: 2px solid #FCA5A5 !important;
    }
    .box-l1 h4 {
        color: #991B1B !important;
    }
    .box-l1 h4 small {
        color: #B91C1C !important;
    }
    .box-l2 {
        background-color: #FEF3C7 !important;
        border: 2px solid #FCD34D !important;
    }
    .box-l2 h4 {
        color: #92400E !important;
    }
    .box-l2 h4 small {
        color: #D97706 !important;
    }
    .box-l3 {
        background-color: #D1FAE5 !important;
        border: 2px solid #6EE7B7 !important;
    }
    .box-l3 h4 {
        color: #065F46 !important;
    }
    .box-l3 h4 small {
        color: #059669 !important;
    }
    .leitner-card {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border-left-width: 4px !important;
    }
    """
    flashcard_theme_css = """
    .flashcard-front, .flashcard-back {
        background-color: #FFFFFF !important;
        border-color: #E2E8F0 !important;
    }
    .card-word {
        color: #1E3A8A !important;
    }
    .card-word-back {
        color: #10B981 !important;
    }
    .card-lang {
        color: #64748B !important;
    }
    .card-hint-text {
        color: #94A3B8 !important;
    }
    """
else: # Följ systemet
    theme_css = """
    /* Standard Ljust */
    .box-l1 {
        background-color: #FEE2E2;
        border: 2px solid #FCA5A5;
    }
    .box-l1 h4 {
        color: #991B1B;
    }
    .box-l1 h4 small {
        color: #B91C1C;
    }
    .box-l2 {
        background-color: #FEF3C7;
        border: 2px solid #FCD34D;
    }
    .box-l2 h4 {
        color: #92400E;
    }
    .box-l2 h4 small {
        color: #D97706;
    }
    .box-l3 {
        background-color: #D1FAE5;
        border: 2px solid #6EE7B7;
    }
    .box-l3 h4 {
        color: #065F46;
    }
    .box-l3 h4 small {
        color: #059669;
    }
    .leitner-card {
        background-color: #FFFFFF;
        color: #1E293B;
        border-left-width: 4px !important;
    }

    /* Mörkt läge media query */
    @media (prefers-color-scheme: dark) {
        .box-l1 {
            background-color: #451a1a !important;
            border: 2px solid #7f1d1d !important;
        }
        .box-l1 h4 {
            color: #fca5a5 !important;
        }
        .box-l1 h4 small {
            color: #ef4444 !important;
        }
        .box-l2 {
            background-color: #45290a !important;
            border: 2px solid #78350f !important;
        }
        .box-l2 h4 {
            color: #fcd34d !important;
        }
        .box-l2 h4 small {
            color: #f59e0b !important;
        }
        .box-l3 {
            background-color: #064e3b !important;
            border: 2px solid #065f46 !important;
        }
        .box-l3 h4 {
            color: #a7f3d0 !important;
        }
        .box-l3 h4 small {
            color: #10b981 !important;
        }
        .leitner-card {
            background-color: #1E293B !important;
            color: #F8FAFC !important;
            border-left-width: 4px !important;
        }
    }
    """
    flashcard_theme_css = """
    @media (prefers-color-scheme: dark) {
        .flashcard-front, .flashcard-back {
            background-color: #1E293B !important;
            border-color: #334155 !important;
        }
        .card-word {
            color: #60A5FA !important;
        }
        .card-word-back {
            color: #34D399 !important;
        }
        .card-lang {
            color: #94A3B8 !important;
        }
        .card-hint-text {
            color: #64748B !important;
        }
    }
    """

# Iniciera den globala CSS-designen
st.markdown(f"""
<style>
/* Global Streamlit UI Polish */
button[data-baseweb="tab"] {{
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
    padding: 10px 18px !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.25s ease !important;
}}
button[data-baseweb="tab"]:hover {{
    color: #3B82F6 !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: #1E3A8A !important;
    background-color: #EFF6FF !important;
    border-bottom: 3px solid #3B82F6 !important;
}}
@media (prefers-color-scheme: dark) {{
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: #60A5FA !important;
        background-color: #1E293B !important;
        border-bottom: 3px solid #60A5FA !important;
    }}
}}

div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] [role="combobox"] {{
    border-radius: 8px !important;
    border: 1px solid #CBD5E1 !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}}
div[data-testid="stTextInput"] input:focus, div[data-testid="stSelectbox"] [role="combobox"]:focus {{
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
}}
@media (prefers-color-scheme: dark) {{
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] [role="combobox"] {{
        border-color: #475569 !important;
    }}
}}

[data-testid="stSidebar"] {{
    background-color: #F8FAFC !important;
}}
@media (prefers-color-scheme: dark) {{
    [data-testid="stSidebar"] {{
        background-color: #0F172A !important;
    }}
}}

.leitner-card {{
    border-radius: 6px;
    padding: 6px 10px;
    margin: 6px 0;
    font-size: 0.85rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    text-align: center;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}
.box-l1, .box-l2, .box-l3 {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0px !important;
    min-height: auto !important;
    margin-bottom: 15px;
}}
{theme_css}

/* Snygg, minimalistisk design för gloslådor utan stora bakgrundsblock */
div[data-testid="stExpander"] .box-l1,
div[data-testid="stExpander"] .box-l2,
div[data-testid="stExpander"] .box-l3 {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0px !important;
    min-height: auto !important;
    margin-bottom: 25px !important;
}}

/* Custom CSS for clickable category cards and list cards */
div[data-testid="element-container"]:has(.folder-card-anchor) + div[data-testid="element-container"] .stButton button {{
    background-color: #EFF6FF !important;
    border: 1px solid #3B82F6 !important;
    border-left: 6px solid #3B82F6 !important;
    border-radius: 10px !important;
    padding: 18px 24px !important;
    font-size: 1.35rem !important;
    font-weight: bold !important;
    color: #1E3A8A !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 10px rgba(59, 130, 246, 0.05) !important;
    margin-bottom: 12px !important;
    display: block !important;
    height: auto !important;
}}

div[data-testid="element-container"]:has(.folder-card-anchor) + div[data-testid="element-container"] .stButton button:hover {{
    background-color: #DBEAFE !important;
    border-color: #2563EB !important;
    box-shadow: 0 6px 15px rgba(59, 130, 246, 0.1) !important;
    transform: translateY(-1px) !important;
}}

div[data-testid="element-container"]:has(.list-card-anchor) + div[data-testid="element-container"] .stButton button {{
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    padding: 16px 20px !important;
    font-size: 1.2rem !important;
    font-weight: bold !important;
    color: #1E3A8A !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
    margin-bottom: 12px !important;
    display: block !important;
    height: auto !important;
}}


.welcome-banner-card {{
    background: linear-gradient(135deg, #eff6ff, #ecfdf5) !important;
    border: 1px solid #bfdbfe !important;
    border-left: 6px solid #3b82f6 !important;
    padding: 20px !important;
    border-radius: 12px !important;
    margin-bottom: 22px !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.05) !important;
}}
.welcome-banner-text {{
    margin: 0 !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    color: #1e3a8a !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    line-height: 1.6 !important;
}}
.login-banner-card {{
    background: linear-gradient(135deg, #eff6ff, #ecfdf5) !important;
    border: 1px solid #bfdbfe !important;
    border-left: 6px solid #3b82f6 !important;
    border-radius: 12px !important;
    padding: 25px !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.05) !important;
    text-align: center !important;
}}
.login-banner-title {{
    margin-top: 0 !important;
    color: #1e3a8a !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    font-weight: 700 !important;
}}
.login-banner-text {{
    color: #475569 !important;
    font-size: 0.95rem !important;
    margin-bottom: 20px !important;
}}

@media (prefers-color-scheme: dark) {{
    .welcome-banner-card {{
        background: linear-gradient(135deg, #1e293b, #064e3b) !important;
        border: 1px solid #334155 !important;
        border-left: 6px solid #10b981 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }}
    .welcome-banner-text {{
        color: #f8fafc !important;
    }}
    .login-banner-card {{
        background: linear-gradient(135deg, #1e293b, #064e3b) !important;
        border: 1px solid #334155 !important;
        border-left: 6px solid #10b981 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }}
    .login-banner-title {{
        color: #60a5fa !important;
    }}
    .login-banner-text {{
        color: #94a3b8 !important;
    }}
}}
div[data-testid="element-container"]:has(.list-card-anchor) + div[data-testid="element-container"] .stButton button:hover {{
    background-color: #F8FAFC !important;
    border-color: #CBD5E1 !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    transform: translateY(-1px) !important;
}}

@media (prefers-color-scheme: dark) {{
    div[data-testid="element-container"]:has(.folder-card-anchor) + div[data-testid="element-container"] .stButton button {{
        background-color: #1E293B !important;
        border: 1px solid #3B82F6 !important;
        border-left: 6px solid #3B82F6 !important;
        color: #60A5FA !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
    }}
    div[data-testid="element-container"]:has(.folder-card-anchor) + div[data-testid="element-container"] .stButton button:hover {{
        background-color: #334155 !important;
        border-color: #60A5FA !important;
    }}
    div[data-testid="element-container"]:has(.list-card-anchor) + div[data-testid="element-container"] .stButton button {{
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        color: #F8FAFC !important;
    }}
    div[data-testid="element-container"]:has(.list-card-anchor) + div[data-testid="element-container"] .stButton button:hover {{
        background-color: #334155 !important;
        border-color: #475569 !important;
    }}
}}


@media (max-width: 768px) {{
    h1 {{
        font-size: 26px !important;
    }}
    .box-l1, .box-l2, .box-l3 {{
        min-height: auto !important;
        padding: 10px !important;
        margin-bottom: 10px !important;
    }}
    div[data-testid="element-container"]:has(.folder-card-anchor) + div[data-testid="element-container"] .stButton button {{
        padding: 14px 18px !important;
        font-size: 1.15rem !important;
    }}
    div[data-testid="element-container"]:has(.list-card-anchor) + div[data-testid="element-container"] .stButton button {{
        padding: 12px 16px !important;
        font-size: 1.0rem !important;
    }}
}}

.quiz-feedback-card {{
    padding: 20px !important;
    border-radius: 12px !important;
    margin-top: 15px !important;
    margin-bottom: 20px !important;
    text-align: center !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
}}
.feedback-correct {{
    background: linear-gradient(135deg, #ECFDF5, #D1FAE5) !important;
    border: 1px solid #A7F3D0 !important;
    border-left: 6px solid #10B981 !important;
    color: #065F46 !important;
}}
.feedback-incorrect {{
    background: linear-gradient(135deg, #FFF5F5, #FEE2E2) !important;
    border: 1px solid #FCA5A5 !important;
    border-left: 6px solid #EF4444 !important;
    color: #991B1B !important;
}}

@keyframes pulse-correct {{
    0% {{ box-shadow: 0 0 0 0px rgba(16, 185, 129, 0.3); }}
    100% {{ box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }}
}}
@keyframes pulse-incorrect {{
    0% {{ box-shadow: 0 0 0 0px rgba(239, 68, 68, 0.3); }}
    100% {{ box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }}
}}

@media (prefers-color-scheme: dark) {{
    .feedback-correct {{
        background: linear-gradient(135deg, #064E3B, #022C22) !important;
        border: 1px solid #047857 !important;
        border-left: 6px solid #10B981 !important;
        color: #A7F3D0 !important;
    }}
    .feedback-incorrect {{
        background: linear-gradient(135deg, #451A1A, #2D0F0F) !important;
        border: 1px solid #991B1B !important;
        border-left: 6px solid #EF4444 !important;
        color: #FCA5A5 !important;
    }}
}}
</style>
</style>
""", unsafe_allow_html=True)


# Kontrollera om eleven befinner sig på Glosbiblioteksskärmen (current_list_name är None)
if st.session_state.current_list_name is None and st.session_state.logged_in_user["name"] != "Lärare":
    st.markdown("---")
    
    # Om ingen kategori är vald, visa mapparna
    if st.session_state.get("selected_category") is None:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e3a8a, #0d9488); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px;">
            <h2 style="margin: 0; font-size: 2rem; font-family: sans-serif;">📚 Välj kategori</h2>
            <p style="margin: 10px 0 0 0; font-size: 1rem; opacity: 0.9;">Välj en mapp för att visa tillgängliga gloslistor.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Hämta alla unika kategorier från biblioteket
        categories_dict = {}
        for name, info in st.session_state.library.items():
            cat = info.get("category", "Övriga listor")
            if cat not in categories_dict:
                categories_dict[cat] = []
            categories_dict[cat].append(name)
            
        if not categories_dict:
            st.info("Det finns inga gloslistor registrerade än. Logga in i Lärarpanelen för att lägga till gloslistor.")
        else:
            # Visa kategorier som klickbara mappar (knappen ÄR själva mappen!)
            for cat_name, list_names in categories_dict.items():
                list_count = len(list_names)
                suffix = "lista" if list_count == 1 else "listor"
                st.markdown('<div class="folder-card-anchor"></div>', unsafe_allow_html=True)
                if st.button(f"📁 {cat_name}  ({list_count} {suffix}) ➔", key=f"select_cat_{cat_name}", use_container_width=True):
                    st.session_state.selected_category = cat_name
                    st.rerun()
    else:
        # En kategori är vald! Visa listor inuti den kategorin
        cat_name = st.session_state.selected_category
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a, #0d9488); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px;">
            <h2 style="margin: 0; font-size: 2rem; font-family: sans-serif;">📁 {cat_name}</h2>
            <p style="margin: 10px 0 0 0; font-size: 1rem; opacity: 0.9;">Välj den gloslista du vill träna på.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Knapp för att gå tillbaka till mapp-vyn
        if st.button("⬅ Gå tillbaka till mappar", use_container_width=True):
            st.session_state.selected_category = None
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Hämta listor som tillhör den valda kategorin
        matching_lists = [name for name, info in st.session_state.library.items() if info.get("category", "Övriga listor") == cat_name]
        
        if not matching_lists:
            st.warning("Mappen är tom!")
        else:
            for list_name in matching_lists:
                list_info = st.session_state.library[list_name]
                lang = list_info.get("language", "Spanska")
                word_count = len(list_info.get("words", []))
                
                # Visa gloslistor som klickbara kort (knappen ÄR själva listkortet!)
                st.markdown('<div class="list-card-anchor"></div>', unsafe_allow_html=True)
                if st.button(f"📄 {list_name}  ({lang} • {word_count} ord) ➔", key=f"select_list_{list_name}", use_container_width=True):
                        st.session_state.current_list_name = list_name
                        st.session_state.words = list_info["words"].copy()
                        st.session_state.target_language = lang
                        reset_progress()
                        st.rerun()
                        
    st.stop() # Avbryt körning här så vi inte ritar upp träningslägena när ingen lista valts!

# Spara gSheets url-namnet
target_lang_name = st.session_state.target_language

# Beräkna fördelning i Leitner-lådorna för den aktiva listan
box1_count = sum(1 for w in st.session_state.words if get_word_box(w["svenska"]) == 1)
box2_count = sum(1 for w in st.session_state.words if get_word_box(w["svenska"]) == 2)
box3_count = sum(1 for w in st.session_state.words if get_word_box(w["svenska"]) == 3)

# Vertikala färgkodade lådor ("Klätterstegen") i sidofältet
st.sidebar.markdown("---")
st.sidebar.subheader("Gloslådor (Klätterstegen)")
st.sidebar.markdown(f"""
<div style='display: flex; flex-direction: column; gap: 8px;'>
    <div style='background-color: #D1FAE5; border-left: 5px solid #10B981; border-radius: 6px; padding: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);'>
        <span style='font-size: 1.1rem;'>🟢</span> <b>Kan bra!</b> (Låda 3)<br>
        <span style='font-size: 1.3rem; font-weight: bold; color: #065F46;'>{box3_count} ord</span>
    </div>
    <div style='background-color: #FEF3C7; border-left: 5px solid #F59E0B; border-radius: 6px; padding: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);'>
        <span style='font-size: 1.1rem;'>🟡</span> <b>På väg</b> (Låda 2)<br>
        <span style='font-size: 1.3rem; font-weight: bold; color: #92400E;'>{box2_count} ord</span>
    </div>
    <div style='background-color: #FEE2E2; border-left: 5px solid #EF4444; border-radius: 6px; padding: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);'>
        <span style='font-size: 1.1rem;'>🔴</span> <b>Ska övas</b> (Låda 1)<br>
        <span style='font-size: 1.3rem; font-weight: bold; color: #991B1B;'>{box1_count} ord</span>
    </div>
</div>
<p style='font-size: 0.75rem; color: gray; margin-top: 5px; text-align: center;'>Ord du kan utantill klättrar upp till den gröna lådan!</p>
""", unsafe_allow_html=True)

# Träningsinställningar i sidofältet
st.sidebar.markdown("---")
st.sidebar.subheader("Träningsinställningar")

direction_label_1 = "Svenska ➔ Målspråk"
direction_label_2 = "Målspråk ➔ Svenska"

def sync_from_sidebar():
    st.session_state.direction_mode = st.session_state.sb_direction
    st.session_state.mn_direction = st.session_state.sb_direction
    reset_progress()

direction = st.sidebar.selectbox(
    "Välj träningsriktning:",
    (direction_label_1, direction_label_2),
    key="sb_direction",
    on_change=sync_from_sidebar,
    help="Välj om du vill öva från svenska till målspråket, eller tvärtom."
)

if st.sidebar.button("Nollställ framsteg", use_container_width=True):
    reset_progress()
    st.toast("Framsteg nollställda!")

# Navigeringsrad längst upp på huvudsidan
col_back_nav, col_curr_list = st.columns([1, 4])
with col_back_nav:
    if st.button("📚 Gloslistor", use_container_width=True, help="Gå tillbaka till biblioteket och välj en annan lista"):
        st.session_state.current_list_name = None
        st.session_state.selected_category = None
        st.rerun()
with col_curr_list:
    st.info(f"👉 Aktiv lista: **{st.session_state.current_list_name}** ({target_lang_name})")

# Snabbval för träningsriktning direkt vid övningen (om eleven missat den i sidomenyn)
st.markdown("---")
col_info, col_sel = st.columns([2, 1])
with col_info:
    st.markdown("<p style='margin-top: 10px; font-weight: bold; color: #475569;'>Snabbval för träningsriktning:</p>", unsafe_allow_html=True)

with col_sel:
    def sync_from_main():
        st.session_state.direction_mode = st.session_state.mn_direction
        st.session_state.sb_direction = st.session_state.mn_direction
        reset_progress()

    st.selectbox(
        "Träningsriktning:",
        ("Svenska ➔ Målspråk", "Målspråk ➔ Svenska"),
        key="mn_direction",
        label_visibility="collapsed",
        on_change=sync_from_main,
    )

# Beräkna fördelningen för den vertikala progressionen på huvudsidan
main_box1 = [w for w in st.session_state.words if get_word_box(w["svenska"]) == 1]
main_box2 = [w for w in st.session_state.words if get_word_box(w["svenska"]) == 2]
main_box3 = [w for w in st.session_state.words if get_word_box(w["svenska"]) == 3]

with st.expander("📦 Se dina gloslådor (Klätterstegen)"):
    st.markdown("""
    Här ser du hur dina ord är fördelade i dina personliga gloslådor.
    Svara rätt i rad för att få ordet att klättra uppför stegen till **Låda 3 (Grön - Kan bra!)**.
    Om du svarar fel faller ordet direkt tillbaka till **Låda 1 (Röd - Ska övas)** så att du kan öva mer på det!
    """)
    
    # Låda 3 (Kan bra! - Överst på stegen)
    st.markdown("<div class='box-l3' style='margin-bottom:12px;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin: 0 0 10px 0;'>🟢 Låda 3 - Kan bra!<br><small style='font-weight:normal; font-size:0.75rem; color:#059669;'>Ord du kan utantill</small></h4>", unsafe_allow_html=True)
    if main_box3:
        cols_l3 = st.columns(4)
        for idx, w in enumerate(main_box3):
            with cols_l3[idx % 4]:
                st.markdown(f"<div class='leitner-card' style='border-left: 4px solid #10B981; margin: 4px 0;'><b>{w['svenska']}</b><br><span style='color:gray; font-size:0.75rem;'>{w['utlandska']}</span></div>", unsafe_allow_html=True)
    else:
        st.caption("Inga ord i Låda 3 än.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Låda 2 (På väg - Mitten på stegen)
    st.markdown("<div class='box-l2' style='margin-bottom:12px;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin: 0 0 10px 0;'>🟡 Låda 2 - På väg<br><small style='font-weight:normal; font-size:0.75rem; color:#D97706;'>Ord du håller på att lära dig</small></h4>", unsafe_allow_html=True)
    if main_box2:
        cols_l2 = st.columns(4)
        for idx, w in enumerate(main_box2):
            with cols_l2[idx % 4]:
                st.markdown(f"<div class='leitner-card' style='border-left: 4px solid #F59E0B; margin: 4px 0;'><b>{w['svenska']}</b><br><span style='color:gray; font-size:0.75rem;'>{w['utlandska']}</span></div>", unsafe_allow_html=True)
    else:
        st.caption("Inga ord i Låda 2 än.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Låda 1 (Ska övas - Botten på stegen)
    st.markdown("<div class='box-l1' style='margin-bottom:12px;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin: 0 0 10px 0;'>🔴 Låda 1 - Ska övas<br><small style='font-weight:normal; font-size:0.75rem; color:#B91C1C;'>Ord du behöver träna mer på</small></h4>", unsafe_allow_html=True)
    if main_box1:
        cols_l1 = st.columns(4)
        for idx, w in enumerate(main_box1):
            with cols_l1[idx % 4]:
                st.markdown(f"<div class='leitner-card' style='border-left: 4px solid #EF4444; margin: 4px 0;'><b>{w['svenska']}</b><br><span style='color:gray; font-size:0.75rem;'>{w['utlandska']}</span></div>", unsafe_allow_html=True)
    else:
        st.caption("Tomt! Snyggt jobbat!")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
# Skapa tab-paneler för de olika träningslägena
tab1, tab2, tab3, tab4 = st.tabs([
    "Flashcards (Se & Öva)",
    "Flervalsquiz (Välj rätt)",
    "Skrivträning (Stava rätt)",
    "Lärarpanel (Skapa & Ladda upp)"
])

# Kontrollera om listan är tom
if not st.session_state.words:
    st.warning("⚠️ Ordlistan är tom! Gå till fliken 'Lärarpanel' för att lägga till glosor.")
else:
    current_word = get_current_word()
    
    # Bestäm källtext och målsvar baserat på vald riktning och språknamn
    direction = st.session_state.direction_mode
    if direction == "Svenska ➔ Målspråk":
        prompt_lang = "svenska"
        target_lang = "utlandska"
        label_prompt = "Svenska"
        label_target = target_lang_name
    else:
        prompt_lang = "utlandska"
        target_lang = "svenska"
        label_prompt = target_lang_name
        label_target = "Svenska"

    # ================= TAB 1: FLASHCARDS =================
    with tab1:
        st.subheader("Träna med digitala ordkort")
        st.markdown("Se det markerade ordet, tänk efter vad det betyder, och klicka direkt på kortet för att vända det.")
        
        # HTML-baserad Flashcard med inbyggd JS-baserad vändning (med inbyggd temakryptering)
        card_html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: transparent;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 250px;
            overflow: hidden;
        }}
        .flashcard-wrapper {{
            perspective: 1000px;
            width: 100%;
            max-width: 460px;
            height: 220px;
            cursor: pointer;
        }}
        .flashcard-inner {{
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
        }}
        .flashcard-wrapper.flipped .flashcard-inner {{
            transform: rotateY(180deg);
        }}
        .flashcard-front, .flashcard-back {{
            position: absolute;
            width: 100%;
            height: 100%;
            -webkit-backface-visibility: hidden;
            backface-visibility: hidden;
            border-radius: 16px;
            border: 2px solid #E2E8F0;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
            box-sizing: border-box;
            background-color: #FFFFFF;
            transition: box-shadow 0.3s ease;
        }}
        .flashcard-wrapper:hover .flashcard-front,
        .flashcard-wrapper:hover .flashcard-back {{
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}
        .card-word {{
            font-size: 2.2rem;
            font-weight: bold;
            margin: 0;
            color: #1E3A8A;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        .card-word-back {{
            font-size: 2.2rem;
            font-weight: bold;
            margin: 0;
            color: #10B981;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        .card-lang {{
            color: #64748B;
            font-size: 0.9rem;
            margin-top: 8px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        .card-hint-text {{
            color: #94A3B8;
            font-size: 0.8rem;
            margin: 0;
            position: absolute;
            bottom: 12px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        
        {flashcard_theme_css}
        
        </style>
        </head>
        <body>
        <div class="flashcard-wrapper" id="card" onclick="toggleFlip()">
            <div class="flashcard-inner">
                <div class="flashcard-front">
                    <p class="card-word">{current_word[prompt_lang]}</p>
                    <p class="card-lang">({label_prompt})</p>
                    <p class="card-hint-text">🖱️ Klicka på kortet för att vända</p>
                </div>
                <div class="flashcard-back" style="transform: rotateY(180deg);">
                    <p class="card-word-back">{current_word[target_lang]}</p>
                    <p class="card-lang">({label_target})</p>
                    <p class="card-hint-text">🖱️ Klicka för att vända tillbaka</p>
                </div>
            </div>
        </div>
        <script>
        function toggleFlip() {{
            const card = document.getElementById('card');
            card.classList.toggle('flipped');
        }}
        </script>
        </body>
        </html>
        """
        components.html(card_html_code, height=270)
        
        if st.button("Nästa kort ➔", use_container_width=True):
            if st.session_state.get("logged_in_user") and st.session_state.logged_in_user["name"] not in ["Gäst", "Lärare"]:
                st.session_state.leitner_boxes["_stats_flashcard_total"] = st.session_state.leitner_boxes.get("_stats_flashcard_total", 0) + 1
            next_word()
            st.rerun()

    # ================= TAB 2: FLERVALSQUIZ ================
    with tab2:
        st.subheader("Testa dina kunskaper")
        st.markdown("Klicka på rätt alternativ för att svara. Svaret sparas och appen går vidare automatiskt.")
        
        # Skapa alternativ om de inte redan finns för nuvarande fråga
        if not st.session_state.quiz_options or len(st.session_state.quiz_options) < 4:
            correct_ans = current_word[target_lang]
            other_words = [w[target_lang] for w in st.session_state.words if w[target_lang] != correct_ans]
            if len(other_words) >= 3:
                distractors = random.sample(other_words, 3)
            else:
                distractors = other_words + ["time", "year", "people", "way"][:3 - len(other_words)]
            options = distractors + [correct_ans]
            random.shuffle(options)
            st.session_state.quiz_options = options
            st.session_state.quiz_correct_index = options.index(correct_ans)
            st.session_state.quiz_answered_option = None
            st.session_state.quiz_scored = False

        st.markdown(f"Vad betyder: **{current_word[prompt_lang]}**?")
        
        correct_ans = current_word[target_lang]
        
        # Rendera valmöjligheterna
        if st.session_state.quiz_answered_option is None:
            # Eleven har inte valt något än -> aktivt val
            selected_option = st.radio(
                "Alternativ:", 
                st.session_state.quiz_options, 
                index=None, 
                key=f"quiz_radio_select_{st.session_state.current_index}",
                label_visibility="collapsed"
            )
            
            if selected_option is not None:
                st.session_state.quiz_answered_option = selected_option
                st.rerun()
        else:
            # Eleven har valt -> Visa låsta alternativ
            selected_option = st.session_state.quiz_answered_option
            selected_idx = st.session_state.quiz_options.index(selected_option)
            st.radio(
                "Alternativ:", 
                st.session_state.quiz_options, 
                index=selected_idx, 
                disabled=True, 
                key=f"quiz_radio_disabled_{st.session_state.current_index}",
                label_visibility="collapsed"
            )
            
            # Kör rättning och poängräkning en gång
            if not st.session_state.quiz_scored:
                st.session_state.total_answered += 1
                
                # Spara statistik om inloggad elev
                if st.session_state.get("logged_in_user") and st.session_state.logged_in_user["name"] not in ["Gäst", "Lärare"]:
                    st.session_state.leitner_boxes["_stats_quiz_total"] = st.session_state.leitner_boxes.get("_stats_quiz_total", 0) + 1
                    if selected_option == correct_ans:
                        st.session_state.leitner_boxes["_stats_quiz_correct"] = st.session_state.leitner_boxes.get("_stats_quiz_correct", 0) + 1
                
                # Leitner och försök
                if selected_option == correct_ans:
                    st.session_state.score += 1
                    st.session_state.failed_attempts[current_word["svenska"]] = 0
                    update_word_box(current_word["svenska"], True)
                else:
                    st.session_state.failed_attempts[current_word["svenska"]] = st.session_state.failed_attempts.get(current_word["svenska"], 0) + 1
                    update_word_box(current_word["svenska"], False)
                
                st.session_state.quiz_scored = True
                
                # Spara framsteg asynkront i bakgrunden vid svar
                if st.session_state.get("logged_in_user") and st.session_state.logged_in_user["name"] not in ["Gäst", "Lärare"]:
                    save_user_progress_to_db(async_save=True)
            
            # Rendera flashy feedback-kort
            is_correct = (selected_option == correct_ans)
            if is_correct:
                st.markdown(f"""
                <div class="quiz-feedback-card feedback-correct" style="animation: pulse-correct 1s infinite alternate;">
                    <h3 style="margin: 0; font-size: 1.35rem;">🎉 Rätt svar!</h3>
                    <p style="margin: 8px 0 0 0;"><b>{current_word[prompt_lang]}</b> betyder mycket riktigt <b>{correct_ans}</b>.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="quiz-feedback-card feedback-incorrect" style="animation: pulse-incorrect 1s infinite alternate;">
                    <h3 style="margin: 0; font-size: 1.35rem;">❌ Tyvärr fel</h3>
                    <p style="margin: 8px 0 0 0;">Det rätta svaret är: <b>{correct_ans}</b></p>
                </div>
                """, unsafe_allow_html=True)

            # Visa inlärningsstrategi om eleven svarat fel flera gånger (>= 2)
            failed_count_quiz = st.session_state.failed_attempts.get(current_word["svenska"], 0)
            if failed_count_quiz >= 2:
                st.info(f"💡 **Behöver du hjälp att minnas?** Prova den här strategin för ordet:\n\n{get_strategy_tip(current_word, target_lang_name)}")

            # Rendera en synlig och snygg knapp/indikator med JS-auto-klicker
            if st.button("Går vidare automatiskt... ➔", key="next_quiz_auto", use_container_width=True):
                next_word()
                st.rerun()
                
            # JS auto-klicker
            components.html(
                """
                <script>
                setTimeout(function() {
                    var buttons = window.parent.document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        if (buttons[i].textContent.includes('Går vidare')) {
                            buttons[i].click();
                            break;
                        }
                    }
                }, 1800); // 1.8 sekunder
                </script>
                """,
                height=0,
                width=0
            )

    # ================= TAB 3: SKRIVTRÄNING =================
    with tab3:
        st.subheader("Skriv och stava rätt")
        st.markdown("Aktiv återkallning är den mest effektiva metoden för att lära sig glosor utantill.")
        st.markdown(f"Översätt ordet: <h3 style='display:inline;'>{current_word[prompt_lang]}</h3>", unsafe_allow_html=True)
        
        # Initiera write_correct_answered och write_feedback i session_state om de saknas
        if "write_correct_answered" not in st.session_state:
            st.session_state.write_correct_answered = False
        if "write_feedback" not in st.session_state:
            st.session_state.write_feedback = None

        # Dynamisk knapp-etikett för Dubbelt Enter-flödet (TOPRA-modellen)
        button_label = "Nästa ord ➔ [Tryck på Enter igen]" if st.session_state.write_correct_answered else "Rätta mitt svar [Enter]"
        
        # Färga textfältet grönt vid rätt svar
        if "write_correct_answered" in st.session_state and st.session_state.write_correct_answered:
            st.markdown("""
            <style>
            /* Ljust läge */
            div[data-testid="stTextInput"] input {
                background-color: #D1FAE5 !important;
                color: #065F46 !important;
                border: 2px solid #10B981 !important;
                font-weight: bold !important;
            }
            /* Mörkt läge */
            @media (prefers-color-scheme: dark) {
                div[data-testid="stTextInput"] input {
                    background-color: #064e3b !important;
                    color: #a7f3d0 !important;
                    border: 2px solid #059669 !important;
                }
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Om användaren uttryckligen har valt mörkt läge i sidopanelen
            if "theme_mode" in st.session_state and st.session_state.theme_mode == "Mörkt läge":
                st.markdown("""
                <style>
                div[data-testid="stTextInput"] input {
                    background-color: #064e3b !important;
                    color: #a7f3d0 !important;
                    border: 2px solid #059669 !important;
                    font-weight: bold !important;
                }
                </style>
                """, unsafe_allow_html=True)

        # Form för enter-stöd vid rättning (TOPRA-modellen)
        with st.form("write_form"):
            # Håll fältet aktivt så att användaren kan trycka Enter igen för att gå vidare till nästa ord (TOPRA)
            user_input = st.text_input(
                "Skriv din översättning här:", 
                key=f"write_input_{st.session_state.current_index}", 
                placeholder="Stava noggrant..."
            )
            col1, col2 = st.columns(2)
            with col1:
                check_write = st.form_submit_button(button_label, use_container_width=True, type="primary" if st.session_state.write_correct_answered else "secondary")
            with col2:
                hint_btn = st.form_submit_button("💡 Få en ledtråd", use_container_width=True, disabled=st.session_state.write_correct_answered)
                
        # JavaScript-hack för att automatiskt bibehålla tangentbordsfokus i skrivrutan (TOPRA-modellen)
        components.html(
            f"""
            <script>
            setTimeout(function() {{
                var inputs = window.parent.document.querySelectorAll('div[data-testid="stTextInput"] input');
                if (inputs.length > 0) {{
                    inputs[inputs.length - 1].focus();
                }}
            }}, 100);
            </script>
            """,
            height=0,
            width=0,
        )
                
        # Hantera ledtråd
        target_word = current_word[target_lang]
        if hint_btn:
            if st.session_state.hint_count < len(target_word):
                st.session_state.hint_count += 1
                st.rerun()
                
        if st.session_state.hint_count > 0:
            hint_text = target_word[:st.session_state.hint_count] + "_" * (len(target_word) - st.session_state.hint_count)
            st.info(f"Ledtråd: `{hint_text}` (visar {st.session_state.hint_count} av {len(target_word)} bokstäver)")
            
        # Rätta skrivet svar / Gå vidare
        if check_write:
            # Om ordet redan var rättbesvarat och användaren trycker Enter igen -> Gå till nästa ord
            if st.session_state.write_correct_answered:
                next_word()
                st.session_state.write_correct_answered = False
                st.session_state.write_feedback = None
                st.rerun()
            elif not user_input.strip():
                st.warning("Skriv in ett svar först!")
            else:
                st.session_state.total_answered += 1
                correct_answer = current_word[target_lang].strip().lower()
                student_answer = user_input.strip().lower()
                
                # Tolerera punkter i slutet (var mindre noggrann med ord som slutar med punkter)
                clean_correct = correct_answer.rstrip('. ').strip()
                clean_student = student_answer.rstrip('. ').strip()
                
                if st.session_state.get("logged_in_user") and st.session_state.logged_in_user["name"] not in ["Gäst", "Lärare"]:
                    st.session_state.leitner_boxes["_stats_write_total"] = st.session_state.leitner_boxes.get("_stats_write_total", 0) + 1
                    if clean_student == clean_correct:
                        st.session_state.leitner_boxes["_stats_write_correct"] = st.session_state.leitner_boxes.get("_stats_write_correct", 0) + 1
                if clean_student == clean_correct:
                    st.session_state.score += 1
                    st.session_state.failed_attempts[current_word["svenska"]] = 0 # Nollställ försök vid rätt svar
                    update_word_box(current_word["svenska"], True) # Uppdatera Leitner-boxen
                    st.session_state.write_correct_answered = True # Aktivera flödet för Dubbelt Enter!
                    st.session_state.write_feedback = {
                        "type": "success",
                        "text": f"🎉 Strålande! **{current_word[prompt_lang]}** stavas mycket riktigt **{target_word}**."
                    }
                    st.rerun()
                else:
                    st.session_state.failed_attempts[current_word["svenska"]] = st.session_state.failed_attempts.get(current_word["svenska"], 0) + 1
                    update_word_box(current_word["svenska"], False) # Svarar man fel flyttas ordet till Låda 1
                    st.session_state.write_correct_answered = False
                    st.session_state.write_feedback = {
                        "type": "error",
                        "text": f"❌ Tyvärr felstavat eller fel ord. Det korrekta svaret är **{target_word}**."
                    }
                    st.rerun()

        # Visa feedback om den finns i session state (TOPRA-modellen feedback persistens)
        if "write_feedback" in st.session_state and st.session_state.write_feedback:
            if st.session_state.write_feedback["type"] == "success":
                st.success(st.session_state.write_feedback["text"])
                st.info("👉 Tryck på **Enter** igen eller klicka på knappen ovan för att gå vidare till nästa ord!")
            elif st.session_state.write_feedback["type"] == "error":
                st.error(st.session_state.write_feedback["text"])
                    
        # Visa inlärningsstrategi om eleven svarat fel flera gånger (>= 2)
        failed_count_write = st.session_state.failed_attempts.get(current_word["svenska"], 0)
        if failed_count_write >= 2:
            st.info(f"💡 **Behöver du hjälp med stavningen?** Prova den här strategin för ordet:\n\n{get_strategy_tip(current_word, target_lang_name)}")
            


    # ================= TAB 4: LÄRARPANEL & LÖSENORDSSKYDD =================
    with tab4:
        st.subheader("👩🏫 Lärarpanel (Hantera Glosbiblioteket)")
        
        # Automatisk synkronisering av elevstatistiken när läraren visar fliken
        if st.session_state.get("admin_authenticated"):
            import time
            current_time = time.time()
            last_sync = st.session_state.get("last_users_sync", 0)
            if current_time - last_sync > 5:  # Synkronisera automatiskt var 5:e sekund
                st.session_state.users_list = fetch_users_from_db(st.session_state.gsheets_url)
                st.session_state.last_users_sync = current_time
        
        # Initiera lösenordsstatus i session state
        if "admin_authenticated" not in st.session_state:
            st.session_state.admin_authenticated = False
            
        if not st.session_state.admin_authenticated:
            st.markdown("Denna flik är till för lärare för att lägga till nya veckor eller gloslistor. Skriv in lösenordet för att fortsätta:")
            entered_password = st.text_input("Lösenord:", type="password")
            if st.button("Lås upp lärarpanelen", type="primary"):
                if entered_password == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.success("🔓 Lärarpanelen har låsts upp!")
                    st.rerun()
                else:
                    st.error("❌ Felaktigt lösenord! Försök igen.")
        else:
            st.info("🔓 Du är inloggad som lärare.")
            if st.button("🔒 Logga ut (Lås panelen)"):
                st.session_state.admin_authenticated = False
                if "printable_test" in st.session_state:
                    del st.session_state.printable_test
                st.rerun()
                
            st.markdown("---")
            
            # ================= NY RESTRUKTURERAD LÄRARPANEL =================
            # Dela upp lärarpanelen i två renodlade flikar för bättre översikt
            sub_tab1, sub_tab2 = st.tabs(["📊 Elevstatistik & Progression", "⚙️ Kursadministration & Hantering"])
            
            with sub_tab1:
                st.markdown("### 📊 Elevstatistik & Progression")
                st.markdown("Följ dina elevers framsteg, aktivitet och precision i realtid. Statistiken uppdateras automatiskt.")
                
                if not st.session_state.gsheets_url:
                    st.warning("⚠️ Ingen molndatabas ansluten. Gå till fliken 'Kursadministration & Hantering' för att ansluta kalkylarket.")
                else:
                    if st.session_state.users_list:
                        # Initiera aggregat
                        student_data = []
                        total_questions = 0
                        total_mastered = 0
                        
                        student_names = []
                        student_totals = []
                        student_scores = []
                        
                        total_box1 = 0
                        total_box2 = 0
                        total_box3 = 0
                        
                        total_fc = 0
                        total_qz = 0
                        total_qz_corr = 0
                        total_wr = 0
                        total_wr_corr = 0
                        
                        exercise_data = []
                        
                        def safe_str(val):
                            if isinstance(val, list):
                                return str(val[0]) if val else ""
                            return str(val)

                        def safe_int(val):
                            if isinstance(val, list):
                                val = val[0] if val else 0
                            try:
                                return int(float(val))
                            except:
                                return 0
                        
                        for u in st.session_state.users_list:
                            name = safe_str(u.get("name", ""))
                            group = safe_str(u.get("group", ""))
                            pin = safe_str(u.get("pin", ""))
                            last_saved_val = safe_str(u.get("last_saved", ""))
                            if last_saved_val and len(last_saved_val) >= 16:
                                last_saved = last_saved_val[:16].replace("T", " ")
                            else:
                                last_saved = "Aldrig"
                                
                            total = safe_int(u.get("total", 0))
                            score = safe_int(u.get("score", 0))
                            
                            # Leitner data
                            leitner_progress = u.get("leitner", {})
                            if not isinstance(leitner_progress, dict):
                                leitner_progress = {}
                                
                            # Beräkna bemästrade (Låda 3) - uteslut statistiknycklar
                            bemastrade = sum(1 for k, v in leitner_progress.items() if not k.startswith("_stats_") and safe_int(v) == 3)
                            
                            # Räkna lådfördelning
                            for k, v in leitner_progress.items():
                                if k.startswith("_stats_"):
                                    continue
                                val = safe_int(v)
                                if val == 1:
                                    total_box1 += 1
                                elif val == 2:
                                    total_box2 += 1
                                elif val == 3:
                                    total_box3 += 1
                                    
                            # Övningsspecifik statistik
                            fc_val = safe_int(leitner_progress.get("_stats_flashcard_total", 0))
                            qz_val = safe_int(leitner_progress.get("_stats_quiz_total", 0))
                            qz_corr_val = safe_int(leitner_progress.get("_stats_quiz_correct", 0))
                            wr_val = safe_int(leitner_progress.get("_stats_write_total", 0))
                            wr_corr_val = safe_int(leitner_progress.get("_stats_write_correct", 0))
                            
                            total_fc += fc_val
                            total_qz += qz_val
                            total_qz_corr += qz_corr_val
                            total_wr += wr_val
                            total_wr_corr += wr_corr_val
                            
                            qz_acc = f"{int((qz_corr_val / qz_val) * 100)}%" if qz_val > 0 else "-"
                            wr_acc = f"{int((wr_corr_val / wr_val) * 100)}%" if wr_val > 0 else "-"
                            
                            exercise_data.append({
                                "Elev": name,
                                "Klass": group,
                                "Flashcards (visningar)": fc_val,
                                "Flervalsquiz (svar)": qz_val,
                                "Flervalsquiz (rätt)": qz_corr_val,
                                "Flervalsquiz (precision)": qz_acc,
                                "Skrivträning (svar)": wr_val,
                                "Skrivträning (rätt)": wr_corr_val,
                                "Skrivträning (precision)": wr_acc
                            })
                            
                            total_questions += total
                            total_mastered += bemastrade
                            
                            acc = f"{int((score / total) * 100)}%" if total > 0 else "0%"
                            
                            student_data.append({
                                "Elev": name,
                                "Klass/Grupp": group,
                                "PIN-kod": pin,
                                "Senaste Aktivitet": last_saved,
                                "Svarade Frågor": total,
                                "Rätt Svar": score,
                                "Precision": acc,
                                "Bemästrade Glosor (Låda 3)": bemastrade
                            })
                            
                            student_names.append(name)
                            student_totals.append(total)
                            student_scores.append(score)
                            
                        # Klassrumssammanfattning
                        st.markdown("#### 🎯 Klassrumssammanfattning")
                        col_m1, col_m2, col_m3 = st.columns(3)
                        with col_m1:
                            st.metric("Registrerade elever", len(st.session_state.users_list))
                        with col_m2:
                            st.metric("Svarade frågor (totalt)", total_questions)
                        with col_m3:
                            st.metric("Bemästrade glosor", total_mastered)
                            
                        st.markdown("---")
                        
                        # Grafiska diagram
                        st.markdown("#### 📈 Grafisk Översikt")
                        col_chart1, col_chart2 = st.columns(2)
                        
                        with col_chart1:
                            st.markdown("<p style='font-weight: bold; text-align: center; color: #1E3A8A;'>📦 Fördelning av gloslådor (Klätterstegen)</p>", unsafe_allow_html=True)
                            box_df = pd.DataFrame({
                                "Antal ord i klassen": [total_box1, total_box2, total_box3]
                            }, index=["🔴 Låda 1 (Ska övas)", "🟡 Låda 2 (På väg)", "🟢 Låda 3 (Kan bra)"])
                            st.bar_chart(box_df, color="#3B82F6")
                            st.caption("Visar det sammanlagda antalet ord som eleverna har placerade i de olika lådorna.")
                            
                        with col_chart2:
                            st.markdown("<p style='font-weight: bold; text-align: center; color: #1E3A8A;'>⚡ Elevaktivitet och Rätt svar</p>", unsafe_allow_html=True)
                            if student_names:
                                chart_df = pd.DataFrame({
                                    "Svarade frågor": student_totals,
                                    "Rätt svar": student_scores
                                }, index=student_names)
                                st.bar_chart(chart_df)
                            st.caption("Jämför antalet besvarade frågor och antalet rätta svar per elev.")
                            
                        st.markdown("---")
                        
                        # Fördelning av övningsform
                        st.markdown("#### 🔄 Aktivitet per övningsform")
                        col_ex_info, col_ex_chart = st.columns([1, 1])
                        
                        with col_ex_info:
                            st.markdown("**Sammanlagda svar per övning:**")
                            st.markdown(f"- 🎴 **Flashcard-visningar:** `{total_fc}` st")
                            st.markdown(f"- 🎯 **Flervalsquiz-svar:** `{total_qz}` st *(Rätt: {total_qz_corr} st)*")
                            st.markdown(f"- ✍️ **Skrivtränings-svar:** `{total_wr}` st *(Rätt: {total_wr_corr} st)*")
                            
                            qz_overall_acc = f"{int((total_qz_corr / total_qz) * 100)}%" if total_qz > 0 else "-"
                            wr_overall_acc = f"{int((total_wr_corr / total_wr) * 100)}%" if total_wr > 0 else "-"
                            st.markdown(f"**Genomsnittlig precision i klassen:**")
                            st.markdown(f"- Flervalsquiz: **{qz_overall_acc}**")
                            st.markdown(f"- Skrivträning: **{wr_overall_acc}**")
                            
                        with col_ex_chart:
                            ex_totals = [total_fc, total_qz, total_wr]
                            ex_df = pd.DataFrame({
                                "Aktivitet": ex_totals
                            }, index=["Flashcards", "Flervalsquiz", "Skrivträning"])
                            st.bar_chart(ex_df, color="#10B981")
                        
                        st.markdown("---")
                        
                        # Detaljerad elevlista
                        st.markdown("#### 📁 Detaljerad elevlista")
                        st.caption("Elevlistan och statistiken synkroniseras automatiskt var 5:e sekund.")
                        df_students = pd.DataFrame(student_data)
                        st.dataframe(df_students, use_container_width=True)
                        
                        # Detaljerad övningsmetodslista
                        st.markdown("#### 📊 Övningsmetoder per elev")
                        df_exercises = pd.DataFrame(exercise_data)
                        st.dataframe(df_exercises, use_container_width=True)
                        
                        if st.button("🔄 Synkronisera elevlista", key="sync_user_list_btn"):
                            fetch_users_from_db.clear()
                            st.session_state.users_list = fetch_users_from_db(st.session_state.gsheets_url)
                            st.success("Elevlistan har synkroniserats!")
                            st.rerun()
                    else:
                        st.info("Inga elever registrerade än. Använd administrationsfliken för att lägga till din första elev!")
            
            with sub_tab2:
                st.markdown("### ⚙️ Kursadministration & Hantering")
                st.markdown("Administrera elevkonton, lägg till/ta bort gloslistor, anslut kalkylark och generera prov.")
                
                # ================= SEKTION: ELEV- & KONTOHANTERING =================
                st.markdown("#### 👥 Elev- & Kontohantering (Molndatabas)")
                st.markdown("Skapa nya elevkonton här. Löpande resultat sparas automatiskt i kalkylarket.")
                
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    new_student_name = st.text_input("Namn på elev:", placeholder="t.ex. Johan Andersson", key="admin_add_student_name")
                    new_student_class = st.text_input("Klass/Grupp:", placeholder="t.ex. Klass 7A", key="admin_add_student_group")
                with col_u2:
                    new_student_pin = st.text_input("Välj 4-siffrig PIN-kod (endast siffror):", max_chars=4, placeholder="t.ex. 1234", key="admin_add_student_pin")
                
                if st.button("👥 Skapa elevkonto", type="primary", use_container_width=True):
                    if not new_student_name.strip() or not new_student_pin.strip() or not new_student_class.strip():
                        st.error("⚠️ Alla fält (Namn, Klass och PIN-kod) måste fyllas i!")
                    elif not new_student_pin.strip().isdigit() or len(new_student_pin.strip()) != 4:
                        st.error("⚠️ PIN-koden måste bestå av exakt 4 siffror!")
                    else:
                        with st.spinner("Skapar konto i databasen..."):
                            success, msg = create_user_in_db(new_student_name, new_student_pin, new_student_class)
                            if success:
                                st.success(f"🎉 {msg}")
                                fetch_users_from_db.clear()
                                st.session_state.users_list = fetch_users_from_db(st.session_state.gsheets_url)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
                
                st.markdown("---")
                
                # ================= SEKTION: UTSKRIFTSBART GLOSFÖRHÖR =================
                st.markdown("#### 🖨️ Skapa utskriftsbart glosförhör")
                st.markdown("Generera ett professionellt provblad i PDF eller utskriftsformat baserat på den valda gloslistan.")
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    quiz_title = st.text_input("Provrubrik på provbladet:", value=f"Glosförhör - {target_lang_name}")
                    quiz_direction = st.selectbox(
                        "Provriktning:",
                        ["Svenska ➔ Målspråk", "Målspråk ➔ Svenska", "Blandat (slumpat)"],
                        key="admin_quiz_direction"
                    )
                with col_p2:
                    max_words = len(st.session_state.words)
                    quiz_count = st.selectbox(
                        "Antal glosor i förhöret:",
                        ["Alla"] + [i for i in [5, 10, 15, 20, 25, 30, 40, 50] if i <= max_words],
                        index=0,
                        key="admin_quiz_count"
                    )
                    include_answers = st.checkbox("Skapa facit-sida också (separat sida)", value=True, key="admin_quiz_include_answers")
                    
                if st.button("📄 Generera utskriftsklart förhör", type="primary", use_container_width=True):
                    if not st.session_state.words:
                        st.error("Det finns inga glosor i din lista att generera prov av!")
                    else:
                        # Blanda glosorna och begränsa antal
                        test_words = st.session_state.words.copy()
                        random.shuffle(test_words)
                        if quiz_count != "Alla":
                            test_words = test_words[:int(quiz_count)]
                            
                        # Pre-generera prompt_word och answer_word för konsistens
                        for w in test_words:
                            if quiz_direction == "Svenska ➔ Målspråk":
                                w["prompt_word"] = w["svenska"]
                                w["answer_word"] = w["utlandska"]
                            elif quiz_direction == "Målspråk ➔ Svenska":
                                w["prompt_word"] = w["utlandska"]
                                w["answer_word"] = w["svenska"]
                            else:
                                if random.choice([True, False]):
                                    w["prompt_word"] = w["svenska"] + f" (➔ {target_lang_name})"
                                    w["answer_word"] = w["utlandska"]
                                else:
                                    w["prompt_word"] = w["utlandska"] + " (➔ Svenska)"
                                    w["answer_word"] = w["svenska"]
                        
                        st.session_state.quiz_test_words = test_words
                        st.session_state.quiz_title_val = quiz_title
                        st.session_state.quiz_include_answers = include_answers
                        st.session_state.quiz_target_lang = target_lang_name
                        
                        test_html = ""
                        facit_html = ""
                        
                        # CSS för utskrift
                        style_block = """
                        <style>
                        @media print {
                            header, footer, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stToolbar"], .stTabs, button, hr, .print-hide {
                                display: none !important;
                                height: 0 !important;
                                padding: 0 !important;
                                margin: 0 !important;
                            }
                            body, .stApp, .main, .block-container, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
                                height: auto !important;
                                min-height: 0 !important;
                                max-height: none !important;
                                overflow: visible !important;
                                padding: 0 !important;
                                margin: 0 !important;
                                width: 100% !important;
                                display: block !important;
                            }
                            body * {
                                visibility: hidden !important;
                            }
                            .print-container, .print-container * {
                                visibility: visible !important;
                            }
                            .print-container {
                                position: absolute !important;
                                left: 0 !important;
                                top: 0 !important;
                                width: 100% !important;
                                height: auto !important;
                                border: none !important;
                                box-shadow: none !important;
                                padding: 0 !important;
                                margin: 0 !important;
                                background: white !important;
                                color: black !important;
                            }
                            .page-break {
                                page-break-before: always !important;
                            }
                        }
                        .print-container {
                            background-color: white;
                            color: black;
                            padding: 40px;
                            border: 1px solid #ddd;
                            border-radius: 5px;
                            font-family: 'Courier New', Courier, monospace, Arial, sans-serif;
                            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                            margin-top: 20px;
                            margin-bottom: 20px;
                        }
                        .print-title {
                            font-size: 26px;
                            font-weight: bold;
                            text-align: center;
                            margin-bottom: 30px;
                            text-transform: uppercase;
                            letter-spacing: 1px;
                        }
                        .print-student-info {
                            margin-bottom: 35px;
                            font-size: 15px;
                            line-height: 1.8;
                        }
                        .info-line {
                            border-bottom: 1px solid black;
                            display: inline-block;
                            width: 180px;
                            margin-right: 20px;
                        }
                        .quiz-table {
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 20px;
                        }
                        .quiz-row {
                            border-bottom: 1px dashed #bbb;
                            height: 50px;
                        }
                        .quiz-num {
                            width: 50px;
                            font-weight: bold;
                            font-size: 18px;
                        }
                        .quiz-prompt {
                            width: 250px;
                            font-size: 18px;
                        }
                        .quiz-answer-line {
                            border-bottom: 1px solid #000;
                            display: inline-block;
                            width: 300px;
                            height: 25px;
                        }
                        .quiz-answer-text {
                            font-size: 18px;
                            font-weight: bold;
                            color: #d32f2f;
                        }
                        </style>
                        """
                        
                        test_html += style_block
                        test_html += "<div class='print-container'>"
                        test_html += f"<div class='print-title'>{quiz_title}</div>"
                        test_html += f"""
                        <div class='print-student-info'>
                            Elevens namn: <span class='info-line'></span>
                            Klass/Grupp:  <span class='info-line'></span>
                            Datum:        <span class='info-line'></span>
                            <br>
                            <b>Poäng: ________ av {len(test_words)} rätt</b>
                        </div>
                        """
                        test_html += "<table class='quiz-table'>"
                        for idx, w in enumerate(test_words, 1):
                            p_word = w["prompt_word"]
                            test_html += f"""
                            <tr class='quiz-row'>
                                <td class='quiz-num'>{idx}.</td>
                                <td class='quiz-prompt'>{p_word}</td>
                                <td><span class='quiz-answer-line'></span></td>
                            </tr>
                            """
                        test_html += "</table>"
                        test_html += "</div>"
                        
                        if include_answers:
                            facit_html += "<div class='print-container page-break'>"
                            facit_html += f"<div class='print-title'>FACIT: {quiz_title}</div>"
                            facit_html += "<table class='quiz-table'>"
                            for idx, w in enumerate(test_words, 1):
                                p_word = w["prompt_word"]
                                a_word = w["answer_word"]
                                facit_html += f"""
                                <tr class='quiz-row'>
                                    <td class='quiz-num'>{idx}.</td>
                                    <td class='quiz-prompt' style='color:#555;'>Fråga: <b>{p_word}</b></td>
                                    <td>Svar: <span class='quiz-answer-text'>{a_word}</span></td>
                                </tr>
                                """
                            facit_html += "</table>"
                            facit_html += "</div>"
                            
                        st.session_state.printable_test = test_html + facit_html
                        st.toast("Glosförhör har genererats!")
                        st.rerun()
                        
                # Visa förhandsgranskning om det finns skapat
                if "printable_test" in st.session_state:
                    st.success("📝 Utskriftsklart förhör finns redo nedan!")
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if "quiz_test_words" in st.session_state:
                            pdf_data = generate_pdf_bytes(
                                st.session_state.quiz_test_words,
                                st.session_state.quiz_title_val,
                                st.session_state.quiz_target_lang,
                                st.session_state.quiz_include_answers
                            )
                            st.download_button(
                                label="📥 Ladda ner förhör som PDF",
                                data=bytes(pdf_data),
                                file_name=f"{st.session_state.quiz_title_val.replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                    with col_b2:
                        if st.button("❌ Radera genererat förhör", use_container_width=True, key="del_print_test"):
                            del st.session_state.printable_test
                            st.rerun()
                            
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(clean_html(st.session_state.printable_test), unsafe_allow_html=True)
                    
                st.markdown("---")
                
                # ================= SEKTION: LÄGG TILL NY LISTA =================
                st.markdown("#### ➕ Lägg till en ny gloslista i biblioteket")
                new_list_title = st.text_input("Vad ska denna gloslista heta i biblioteket?", placeholder="t.ex. Spanska - Kapitel 1", key="add_list_title")
                new_list_lang = st.text_input("Vilket språk övar eleverna på i denna lista?", placeholder="t.ex. Spanska", key="add_list_lang")
                new_list_category = st.text_input("Vilken mapp/kategori ska listan tillhöra?", placeholder="t.ex. Spanska nybörjare, Spanska fortsättning...", key="add_list_category")
                
                st.markdown("**Hur vill du läsa in glosorna?**")
                uploaded_file = st.file_uploader("Metod A: Ladda upp en fil (.txt eller .json)", type=["txt", "json"], key="add_list_file")
                import_text = st.text_area("Metod B: Klistra in fritext direkt", height=120, placeholder="svenska - översättning\nhund - perro\nkatt - gato", key="add_list_text")
                
                if st.button("📥 Lägg till listan i biblioteket", type="primary", use_container_width=True, key="add_list_btn"):
                    if not new_list_title.strip():
                        st.error("Du måste ange ett namn för gloslistan!")
                        st.stop()
                    if not new_list_lang.strip():
                        st.error("Du måste ange vilket språk listan gäller!")
                        st.stop()
                        
                    parsed_words = []
                    
                    if uploaded_file is not None:
                        try:
                            if uploaded_file.name.endswith(".json"):
                                file_data = json.load(uploaded_file)
                                if isinstance(file_data, list) and all("svenska" in w and "utlandska" in w for w in file_data):
                                    parsed_words = file_data
                                else:
                                    st.error("Felaktigt format i JSON-filen!")
                            elif uploaded_file.name.endswith(".txt"):
                                string_data = uploaded_file.read().decode("utf-8")
                                lines = string_data.strip().split("\n")
                                for line_no, line in enumerate(lines, 1):
                                    if not line.strip():
                                        continue
                                    parts = None
                                    for sep in ["-", ":", "="]:
                                        if sep in line:
                                            parts = line.split(sep, 1)
                                            break
                                    if parts and len(parts) == 2:
                                        parsed_words.append({"svenska": parts[0].strip(), "utlandska": parts[1].strip()})
                                    else:
                                        st.error(f"Kunde inte tolka rad {line_no} i filen.")
                                        st.stop()
                        except Exception as e:
                            st.error(f"Kunde inte läsa uppladdad fil: {str(e)}")
                            st.stop()
                    elif import_text.strip():
                        lines = import_text.strip().split("\n")
                        for line_no, line in enumerate(lines, 1):
                            if not line.strip():
                                continue
                            parts = None
                            for sep in ["-", ":", "="]:
                                if sep in line:
                                    parts = line.split(sep, 1)
                                    break
                            if parts and len(parts) == 2:
                                parsed_words.append({"svenska": parts[0].strip(), "utlandska": parts[1].strip()})
                            else:
                                st.error(f"Kunde inte tolka rad {line_no} i textrutan.")
                                st.stop()
                                
                    if parsed_words:
                        st.session_state.library[new_list_title] = {
                            "language": new_list_lang,
                            "category": new_list_category.strip() if new_list_category.strip() else "Övriga listor",
                            "words": parsed_words
                        }
                        st.session_state.current_list_name = new_list_title
                        st.session_state.words = parsed_words
                        st.session_state.target_language = new_list_lang
                        reset_progress()
                        st.success(f"🎉 Lyckades! Listan '{new_list_title}' med {len(parsed_words)} glosor har lagts till i biblioteket!")
                        st.rerun()
                    else:
                        st.warning("Hittade inga giltiga glosor att läsa in.")
                
                st.markdown("---")
                st.markdown("#### 🗑️ Ta bort gloslistor från biblioteket")
                all_lists = list(st.session_state.library.keys())
                for list_name in all_lists:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        list_info = st.session_state.library[list_name]
                        cat = list_info.get("category", "Övriga listor")
                        st.write(f"📁 {list_name} ({list_info['language']}) [Mapp: *{cat}*] — **{len(list_info['words'])}** ord")
                    with col2:
                        if len(all_lists) > 1:
                            if st.button("Radera", key=f"del_list_{list_name}"):
                                st.session_state.library.pop(list_name)
                                if st.session_state.current_list_name == list_name:
                                    new_active = list(st.session_state.library.keys())[0]
                                    st.session_state.current_list_name = new_active
                                    st.session_state.words = st.session_state.library[new_active]["words"].copy()
                                    st.session_state.target_language = st.session_state.library[new_active]["language"]
                                    reset_progress()
                                st.toast(f"Listan '{list_name}' togs bort!")
                                st.rerun()
                        else:
                            st.caption("Kan ej raderas")
