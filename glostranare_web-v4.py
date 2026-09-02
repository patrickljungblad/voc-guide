import streamlit as st
import random
import json
import urllib.request
import streamlit.components.v1 as components

def clean_html(html_str):
    return "\n".join(line.strip() for line in html_str.split("\n"))



# Spårning och förslag på inlärningsstrategier enligt vetenskapliga principer (Mnemonic & Dual Coding)
def get_strategy_tip(word_obj, language):
    sv = word_obj["svenska"].lower().strip()
    ut = word_obj["utlandska"].lower().strip()
    
    # Custom spanska nyckelordstips (Mnemonic Keyword Technique)
    spanish_tips = {
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
        "tid": "**Kognat-tips:** *tiempo* låter som engelskans *tempo* eller *time*. Tempo handlar om tid!"
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

# Sätt sidkonfiguration
st.set_page_config(
    page_title="GlosFlow - Digitala Glostränaren",
    page_icon="🎓",
    layout="centered"
)

# --- LÄRARKONFIGURATION (VALFRITT) ---
ADMIN_PASSWORD = "skola123"

# Du kan förbereda permanenta listor i biblioteket direkt i koden här!
# Detta gör att de alltid ligger laddade för eleverna när hemsidan startas.
PERMANENT_LIBRARY = {
    "Spanska - veckodagar": {
        "language": "Spanska",
        "words": [
            {"svenska": "måndag", "utlandska": "lunes"},
            {"svenska": "tisdag", "utlandska": "martes"},
            {"svenska": "onsdag", "utlandska": "miércoles"},
            {"svenska": "torsdag", "utlandska": "jueves"},
            {"svenska": "fredag", "utlandska": "viernes"},
            {"svenska": "lördag", "utlandska": "sábado"},
            {"svenska": "söndag", "utlandska": "domingo"}
        ]
    },

    "Engelska (Topp 50 vanligaste)": {
        "language": "Engelska",
        "words": [
            {"svenska": "tid", "utlandska": "time"},
            {"svenska": "år", "utlandska": "year"},
            {"svenska": "folk", "utlandska": "people"},
            {"svenska": "sätt", "utlandska": "way"},
            {"svenska": "dag", "utlandska": "day"},
            {"svenska": "sak", "utlandska": "thing"},
            {"svenska": "man", "utlandska": "man"},
            {"svenska": "värld", "utlandska": "world"},
            {"svenska": "liv", "utlandska": "life"},
            {"svenska": "skola", "utlandska": "school"},
            {"svenska": "familj", "utlandska": "family"},
            {"svenska": "student", "utlandska": "student"},
            {"svenska": "land", "utlandska": "country"},
            {"svenska": "problem", "utlandska": "problem"},
            {"svenska": "hand", "utlandska": "hand"},
            {"svenska": "del", "utlandska": "part"},
            {"svenska": "plats", "utlandska": "place"},
            {"svenska": "vecka", "utlandska": "week"},
            {"svenska": "arbete", "utlandska": "work"},
            {"svenska": "system", "utlandska": "system"},
            {"svenska": "grupp", "utlandska": "group"},
            {"svenska": "nummer", "utlandska": "number"},
            {"svenska": "kvinna", "utlandska": "woman"},
            {"svenska": "barn", "utlandska": "child"},
            {"svenska": "sida", "utlandska": "side"},
            {"svenska": "skriva", "utlandska": "write"},
            {"svenska": "läsa", "utlandska": "read"},
            {"svenska": "göra", "utlandska": "do"},
            {"svenska": "se", "utlandska": "see"},
            {"svenska": "gå", "utlandska": "go"},
            {"svenska": "komma", "utlandska": "come"},
            {"svenska": "ha", "utlandska": "have"},
            {"svenska": "ge", "utlandska": "give"},
            {"svenska": "veta", "utlandska": "know"},
            {"svenska": "säga", "utlandska": "say"},
            {"svenska": "ny", "utlandska": "new"},
            {"svenska": "stor", "utlandska": "big"},
            {"svenska": "bra", "utlandska": "good"},
            {"svenska": "först", "utlandska": "first"},
            {"svenska": "vatten", "utlandska": "water"},
            {"svenska": "hus", "utlandska": "house"},
            {"svenska": "vän", "utlandska": "friend"},
            {"svenska": "stad", "utlandska": "city"},
            {"svenska": "bok", "utlandska": "book"},
            {"svenska": "mat", "utlandska": "food"},
            {"svenska": "äpple", "utlandska": "apple"},
            {"svenska": "katt", "utlandska": "cat"},
            {"svenska": "hund", "utlandska": "dog"},
            {"svenska": "liten", "utlandska": "small"},
            {"svenska": "person", "utlandska": "person"}
        ]
    },
    "Spanska (Topp 50 vanligaste)": {
        "language": "Spanska",
        "words": [
            {"svenska": "tid", "utlandska": "tiempo"},
            {"svenska": "år", "utlandska": "año"},
            {"svenska": "folk", "utlandska": "gente"},
            {"svenska": "sätt", "utlandska": "manera"}, # Korrigerat till 'manera' (Sense Selection enligt Paul Nation s. 76)
            {"svenska": "dag", "utlandska": "día"},
            {"svenska": "sak", "utlandska": "cosa"},
            {"svenska": "man", "utlandska": "hombre"},
            {"svenska": "värld", "utlandska": "mundo"},
            {"svenska": "liv", "utlandska": "vida"},
            {"svenska": "skola", "utlandska": "escuela"},
            {"svenska": "familj", "utlandska": "familia"},
            {"svenska": "student", "utlandska": "estudiante"},
            {"svenska": "land", "utlandska": "país"},
            {"svenska": "problem", "utlandska": "problema"},
            {"svenska": "hand", "utlandska": "mano"},
            {"svenska": "del", "utlandska": "parte"},
            {"svenska": "plats", "utlandska": "lugar"},
            {"svenska": "vecka", "utlandska": "semana"},
            {"svenska": "arbete", "utlandska": "trabajo"},
            {"svenska": "system", "utlandska": "sistema"},
            {"svenska": "grupp", "utlandska": "grupo"},
            {"svenska": "nummer", "utlandska": "número"},
            {"svenska": "kvinna", "utlandska": "mujer"},
            {"svenska": "barn", "utlandska": "niño"},
            {"svenska": "sida", "utlandska": "lado"},
            {"svenska": "skriva", "utlandska": "escribir"},
            {"svenska": "läsa", "utlandska": "leer"},
            {"svenska": "göra", "utlandska": "hacer"},
            {"svenska": "se", "utlandska": "ver"},
            {"svenska": "gå", "utlandska": "ir"},
            {"svenska": "komma", "utlandska": "venir"},
            {"svenska": "ha", "utlandska": "tener"},
            {"svenska": "ge", "utlandska": "dar"},
            {"svenska": "veta", "utlandska": "saber"},
            {"svenska": "säga", "utlandska": "decir"},
            {"svenska": "ny", "utlandska": "nuevo"},
            {"svenska": "stor", "utlandska": "grande"},
            {"svenska": "bra", "utlandska": "bueno"},
            {"svenska": "först", "utlandska": "primero"},
            {"svenska": "vatten", "utlandska": "agua"},
            {"svenska": "hus", "utlandska": "casa"},
            {"svenska": "vän", "utlandska": "amigo"},
            {"svenska": "stad", "utlandska": "ciudad"},
            {"svenska": "bok", "utlandska": "libro"},
            {"svenska": "mat", "utlandska": "comida"},
            {"svenska": "äpple", "utlandska": "manzana"},
            {"svenska": "katt", "utlandska": "gato"},
            {"svenska": "hund", "utlandska": "perro"},
            {"svenska": "liten", "utlandska": "pequeño"},
            {"svenska": "person", "utlandska": "persona"}
        ]
    },
    "Spanska nybörjare - v. 36": {
        "language": "Spanska",
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
}

# Initiera biblioteket i session state
if "library" not in st.session_state:
    st.session_state.library = PERMANENT_LIBRARY.copy()

# Initiera aktiv ordlista och målspråk
if "words" not in st.session_state:
    st.session_state.words = st.session_state.library["Engelska (Topp 50 vanligaste)"]["words"].copy()
    st.session_state.target_language = "Engelska"
    st.session_state.current_list_name = "Engelska (Topp 50 vanligaste)"

if "current_list_name" not in st.session_state:
    st.session_state.current_list_name = "Engelska (Topp 50 vanligaste)"

if "direction_mode" not in st.session_state:
    st.session_state.direction_mode = "Svenska ➔ Målspråk"

if "mn_direction" not in st.session_state:
    st.session_state.mn_direction = st.session_state.direction_mode

if "sb_direction" not in st.session_state:
    st.session_state.sb_direction = st.session_state.direction_mode

if "target_language" not in st.session_state:
    st.session_state.target_language = "Engelska"

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

st.markdown("Välkommen till **GlosFlow**! Öva i din egen takt med vetenskapligt beprövade metoder för språkinlärning. Börja med att **välja en gloslista i vänstermenyn** för att starta din träning!")

# Snabbval för träningsriktning direkt vid övningen (om eleven missat den i sidomenyn)
st.markdown("---")
col_info, col_sel = st.columns([2, 1])
with col_info:
    st.markdown("<p style='margin-top: 10px; font-weight: bold; color: #475569;'>⚙️ Snabbval för träningsriktning:</p>", unsafe_allow_html=True)

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

# --- SIDOMENY: GLOSBIBLIOTEK ---
st.sidebar.header("📚 Glosbibliotek")

# Tydlig instruktion för eleverna
st.sidebar.info("👉 **Börja här!** Välj först den gloslista du vill träna på i menyn nedan:")

# Låt eleverna välja gloslista från biblioteket
library_options = list(st.session_state.library.keys())
selected_list = st.sidebar.selectbox(
    "Välj gloslista:",
    library_options,
    index=library_options.index(st.session_state.current_list_name) if st.session_state.current_list_name in library_options else 0,
    help="Här väljer du vilket kapitel eller vilken ordlista du vill träna på just nu."
)

# Om användaren byter lista i biblioteket, ladda in den direkt
if selected_list != st.session_state.current_list_name:
    st.session_state.current_list_name = selected_list
    st.session_state.words = st.session_state.library[selected_list]["words"].copy()
    st.session_state.target_language = st.session_state.library[selected_list]["language"]
    reset_progress()
    st.rerun()

# Hämta namnet på målspråket från session state
target_lang_name = st.session_state.target_language

st.sidebar.markdown("---")

# Visa statistik (Dina framsteg) ovanför träningsinställningarna
st.sidebar.subheader("📊 Dina framsteg")
st.sidebar.write(f"Ord i listan: **{len(st.session_state.words)}**")

if st.session_state.total_answered > 0:
    pct = int((st.session_state.score / st.session_state.total_answered) * 100)
    st.sidebar.write(f"Rätt svar: **{st.session_state.score}** av **{st.session_state.total_answered}** ({pct}%)")
else:
    st.sidebar.write("Rätt svar: **0**")

# Beräkna fördelning i Leitner-lådorna
box1_count = sum(1 for w in st.session_state.words if get_word_box(w["svenska"]) == 1)
box2_count = sum(1 for w in st.session_state.words if get_word_box(w["svenska"]) == 2)
box3_count = sum(1 for w in st.session_state.words if get_word_box(w["svenska"]) == 3)

st.sidebar.markdown("---")
st.sidebar.subheader("📦 Gloslådor (Leitner)")
st.sidebar.markdown(f"""
<div style='display: flex; gap: 4px; margin-bottom: 5px;'>
    <div style='flex: 1; background-color: #FEE2E2; border: 1px solid #FCA5A5; border-radius: 6px; padding: 6px 4px; text-align: center;'>
        <span style='font-size: 1.1rem;'>🔴</span><br>
        <b style='color: #991B1B; font-size: 0.75rem; display:block; margin: 2px 0;'>Låda 1</b>
        <span style='color: #991B1B; font-size: 1rem; font-weight: bold;'>{box1_count}</span>
    </div>
    <div style='flex: 1; background-color: #FEF3C7; border: 1px solid #FCD34D; border-radius: 6px; padding: 6px 4px; text-align: center;'>
        <span style='font-size: 1.1rem;'>🟡</span><br>
        <b style='color: #92400E; font-size: 0.75rem; display:block; margin: 2px 0;'>Låda 2</b>
        <span style='color: #92400E; font-size: 1rem; font-weight: bold;'>{box2_count}</span>
    </div>
    <div style='flex: 1; background-color: #D1FAE5; border: 1px solid #6EE7B7; border-radius: 6px; padding: 6px 4px; text-align: center;'>
        <span style='font-size: 1.1rem;'>🟢</span><br>
        <b style='color: #065F46; font-size: 0.75rem; display:block; margin: 2px 0;'>Låda 3</b>
        <span style='color: #065F46; font-size: 1rem; font-weight: bold;'>{box3_count}</span>
    </div>
</div>
<p style='font-size: 0.75rem; color: gray; margin-top: 5px; text-align: center;'>Svara rätt i rad för att flytta upp ord till gröna lådan!</p>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Träningsinställningar (träningsriktning) placerade nedanför framsteg
st.sidebar.subheader("⚙️ Träningsinställningar")

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

if st.sidebar.button("🔄 Nollställ framsteg", use_container_width=True):
    reset_progress()
    st.toast("Framsteg nollställda!")

st.sidebar.markdown("---")

# Färgtema inställningar
st.sidebar.subheader("🎨 Färgtema")
theme_mode = st.sidebar.selectbox(
    "Välj färgtema:",
    ("Följ systemet", "Ljust läge ☀️", "Mörkt läge 🌙"),
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
    border-radius: 12px;
    padding: 12px;
    min-height: 200px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    margin-bottom: 15px;
}}
{theme_css}
</style>
""", unsafe_allow_html=True)

# Beräkna fördelningen för expandern
main_box1 = [w for w in st.session_state.words if get_word_box(w["svenska"]) == 1]
main_box2 = [w for w in st.session_state.words if get_word_box(w["svenska"]) == 2]
main_box3 = [w for w in st.session_state.words if get_word_box(w["svenska"]) == 3]

with st.expander("📦 Se dina gloslådor (Leitner-systemet)"):
    st.markdown("""
Här ser du hur dina ord är fördelade i dina personliga gloslådor.
Svara rätt flera gånger i följd för att flytta upp ordet till **Låda 3 (Grön)**.
Om du svarar fel faller ordet direkt tillbaka till **Låda 1 (Röd)** så att du får öva mer på det!
""")
    col_l1, col_l2, col_l3 = st.columns(3)
    
    with col_l1:
        st.markdown("<div class='box-l1'>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin: 0 0 10px 0; text-align:center;'>🔴 Låda 1<br><small style='font-weight:normal; font-size:0.75rem;'>Behöver öva mer</small></h4>", unsafe_allow_html=True)
        if main_box1:
            for w in main_box1:
                st.markdown(f"<div class='leitner-card' style='border-left: 4px solid #EF4444;'><b>{w['svenska']}</b><br><span style='color:gray; font-size:0.75rem;'>{w['utlandska']}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align:center; color: #991B1B; font-size:0.8rem; font-style:italic; margin-top:20px;'>Tomt! Snyggt jobbat!</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_l2:
        st.markdown("<div class='box-l2'>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin: 0 0 10px 0; text-align:center;'>🟡 Låda 2<br><small style='font-weight:normal; font-size:0.75rem;'>Kan sisådär</small></h4>", unsafe_allow_html=True)
        if main_box2:
            for w in main_box2:
                st.markdown(f"<div class='leitner-card' style='border-left: 4px solid #F59E0B;'><b>{w['svenska']}</b><br><span style='color:gray; font-size:0.75rem;'>{w['utlandska']}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align:center; color: #92400E; font-size:0.8rem; font-style:italic; margin-top:20px;'>Inga ord här än.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_l3:
        st.markdown("<div class='box-l3'>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin: 0 0 10px 0; text-align:center;'>🟢 Låda 3<br><small style='font-weight:normal; font-size:0.75rem;'>Behärskas väl</small></h4>", unsafe_allow_html=True)
        if main_box3:
            for w in main_box3:
                st.markdown(f"<div class='leitner-card' style='border-left: 4px solid #10B981;'><b>{w['svenska']}</b><br><span style='color:gray; font-size:0.75rem;'>{w['utlandska']}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align:center; color: #065F46; font-size:0.8rem; font-style:italic; margin-top:20px;'>Inga ord avklarade än.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Skapa tab-paneler för de olika träningslägena
tab1, tab2, tab3, tab4 = st.tabs([
    "🎴 Flashcards (Se & Öva)",
    "🎯 Flervalsquiz (Välj rätt)",
    "✍️ Skrivträning (Stava rätt)",
    "👩🏫 Lärarpanel (Skapa & Ladda upp)"
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
            next_word()
            st.rerun()

    # ================= TAB 2: FLERVALSQUIZ ================
    with tab2:
        st.subheader("🎯 Testa dina kunskaper")
        st.markdown("Välj det alternativ som motsvarar rätt översättning.")
        
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
            
        st.markdown(f"Vad betyder: **{current_word[prompt_lang]}**?")
        
        with st.form("quiz_form"):
            selected_option = st.radio("Välj ett alternativ:", st.session_state.quiz_options, index=None)
            submit_quiz = st.form_submit_button("Rätta mitt svar", use_container_width=True)
            
        if submit_quiz:
            if selected_option is None:
                st.warning("Vänligen välj ett alternativ först!")
            else:
                st.session_state.total_answered += 1
                correct_answer = current_word[target_lang]
                if selected_option == correct_answer:
                    st.session_state.score += 1
                    st.session_state.failed_attempts[current_word["svenska"]] = 0 # Nollställ försök vid rätt svar
                    update_word_box(current_word["svenska"], True) # Uppdatera Leitner-boxen
                    st.success(f"🎉 Rätt! **{current_word[prompt_lang]}** betyder **{correct_answer}**.")
                else:
                    st.session_state.failed_attempts[current_word["svenska"]] = st.session_state.failed_attempts.get(current_word["svenska"], 0) + 1
                    update_word_box(current_word["svenska"], False) # Svarar man fel flyttas ordet till Låda 1
                    st.error(f"❌ Fel. Det rätta svaret är **{correct_answer}**.")
                    
        # Visa inlärningsstrategi om eleven svarat fel flera gånger (>= 2)
        failed_count_quiz = st.session_state.failed_attempts.get(current_word["svenska"], 0)
        if failed_count_quiz >= 2:
            st.info(f"💡 **Behöver du hjälp att minnas?** Prova den här strategin för ordet:\n\n{get_strategy_tip(current_word, target_lang_name)}")
            
        if st.button("Nästa fråga ➔", key="next_quiz", use_container_width=True):
            next_word()
            st.rerun()

    # ================= TAB 3: SKRIVTRÄNING =================
    with tab3:
        st.subheader("✍️ Skriv och stava rätt")
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
            if "theme_mode" in st.session_state and st.session_state.theme_mode == "Mörkt läge 🌙":
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
            
        if st.button("Nästa ord ➔", key="next_write", use_container_width=True):
            next_word()
            st.session_state.write_correct_answered = False
            st.session_state.write_feedback = None
            st.rerun()

    # ================= TAB 4: LÄRARPANEL & LÖSENORDSSKYDD =================
    with tab4:
        st.subheader("👩🏫 Lärarpanel (Hantera Glosbiblioteket)")
        
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
            
            # ================= SEKTION: UTSKRIFTSBART GLOSFÖRHÖR =================
            st.markdown("### 🖨️ Skapa utskriftsbart glosförhör")
            st.markdown("Här kan du generera ett professionellt provblad redo att skrivas ut på papper till dina elever. När du klickar på skriv ut-knappen döljs alla webbmenyer automatiskt på utskriften!")
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                quiz_title = st.text_input("Provrubrik på provbladet:", value=f"Glosförhör - {target_lang_name}")
                quiz_direction = st.selectbox(
                    "Provriktning:",
                    ["Svenska ➔ Målspråk", "Målspråk ➔ Svenska", "Blandat (slumpat)"]
                )
            with col_p2:
                max_words = len(st.session_state.words)
                quiz_count = st.selectbox(
                    "Antal glosor i förhöret:",
                    ["Alla"] + [i for i in [5, 10, 15, 20, 25, 30, 40, 50] if i <= max_words],
                    index=0
                )
                include_answers = st.checkbox("Skapa facit-sida också (separat sida)", value=True)
                
            if st.button("📄 Generera utskriftsklart förhör", type="primary", use_container_width=True):
                if not st.session_state.words:
                    st.error("Det finns inga glosor i din lista att generera prov av!")
                else:
                    # Blanda glosorna och begränsa antal
                    test_words = st.session_state.words.copy()
                    random.shuffle(test_words)
                    if quiz_count != "Alla":
                        test_words = test_words[:int(quiz_count)]
                        
                    test_html = ""
                    facit_html = ""
                    
                    # CSS för provbladsutskrift (Extremt robust döljning av Streamlit UI under utskrift)
                    style_block = """
                    <style>
                    @media print {
                        /* Dölj Streamlits egna layoutkomponenter helt */
                        header, footer, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stToolbar"], .stTabs, button, hr, .print-hide {
                            display: none !important;
                            height: 0 !important;
                            padding: 0 !important;
                            margin: 0 !important;
                        }
                        
                        /* Nollställ höjd- och scrollbegränsningar på Streamlits yttre containers */
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
                        
                        /* Dölj ALLA element på hela sidan som standard */
                        body * {
                            visibility: hidden !important;
                        }
                        
                        /* Gör ENBART själva förhörsbehållaren och dess innehåll synligt */
                        .print-container, .print-container * {
                            visibility: visible !important;
                        }
                        
                        /* Positionera förhöret absolut längst upp till vänster på papperet */
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
                    
                    # Generera Elevprov
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
                        # Prompt-hantering baserat på vald riktning
                        if quiz_direction == "Svenska ➔ Målspråk":
                            p_word = w["svenska"]
                        elif quiz_direction == "Målspråk ➔ Svenska":
                            p_word = w["utlandska"]
                        else:
                            # Slumpa riktning per ord i provet
                            if random.choice([True, False]):
                                p_word = w["svenska"] + f" (➔ {target_lang_name})"
                            else:
                                p_word = w["utlandska"] + " (➔ Svenska)"
                                
                        test_html += f"""
                        <tr class='quiz-row'>
                            <td class='quiz-num'>{idx}.</td>
                            <td class='quiz-prompt'>{p_word}</td>
                            <td><span class='quiz-answer-line'></span></td>
                        </tr>
                        """
                    test_html += "</table>"
                    test_html += "</div>"
                    
                    # Generera Lärarfacit
                    if include_answers:
                        facit_html += "<div class='print-container page-break'>"
                        facit_html += f"<div class='print-title'>FACIT: {quiz_title}</div>"
                        facit_html += "<table class='quiz-table'>"
                        for idx, w in enumerate(test_words, 1):
                            facit_html += f"""
                            <tr class='quiz-row'>
                                <td class='quiz-num'>{idx}.</td>
                                <td class='quiz-prompt' style='color:#555;'>Svenska: <b>{w["svenska"]}</b></td>
                                <td>{target_lang_name}: <span class='quiz-answer-text'>{w["utlandska"]}</span></td>
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
                    # Lägg in en knapp som anropar window.print()
                    st.markdown(
                        '<button onclick="window.print()" class="print-hide" style="width:100%; height:42px; border-radius:5px; background-color:#10B981; color:white; border:none; font-weight:bold; cursor:pointer;">🖨️ Öppna utskriftsdialogen</button>',
                        unsafe_allow_html=True
                    )
                with col_b2:
                    if st.button("❌ Radera genererat förhör", use_container_width=True):
                        del st.session_state.printable_test
                        st.rerun()
                        
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Förhandsgranskning av provet
                st.markdown(clean_html(st.session_state.printable_test), unsafe_allow_html=True)
                
            st.markdown("---")
            
            # ================= SEKTION: LÄGG TILL NY LISTA =================
            st.markdown("### ➕ Lägg till en ny gloslista i biblioteket")
            st.markdown("Här kan du bygga upp ett bibliotek av listor för dina elever (t.ex. 'Kapitel 1', 'Vecka 38', 'Engelska - Djur'). De dyker genast upp i elevernas rullgardinsmeny!")
            
            # Unika inställningar för den nya listan
            new_list_title = st.text_input("Vad ska denna gloslista heta i biblioteket?", placeholder="t.ex. Spanska - Kapitel 1")
            new_list_lang = st.text_input("Vilket språk övar eleverna på i denna lista?", placeholder="t.ex. Spanska")
            
            st.markdown("**Hur vill du läsa in glosorna?**")
            uploaded_file = st.file_uploader("Metod A: Ladda upp en fil (.txt eller .json)", type=["txt", "json"])
            import_text = st.text_area("Metod B: Klistra in fritext direkt", height=120, placeholder="svenska - översättning\nhund - perro\nkatt - gato")
            
            if st.button("📥 Lägg till listan i biblioteket", type="primary", use_container_width=True):
                if not new_list_title.strip():
                    st.error("Du måste ange ett namn för gloslistan!")
                    st.stop()
                if not new_list_lang.strip():
                    st.error("Du måste ange vilket språk listan gäller!")
                    st.stop()
                    
                parsed_words = []
                
                # Alternativ 1: Läs in från uppladdad fil
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
                        
                # Alternativ 2: Läs in från fritext (om ingen fil laddats upp)
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
                            
                # Spara listan i biblioteket
                if parsed_words:
                    st.session_state.library[new_list_title] = {
                        "language": new_list_lang,
                        "words": parsed_words
                    }
                    # Gör den nyligen skapade listan till den aktiva listan
                    st.session_state.current_list_name = new_list_title
                    st.session_state.words = parsed_words
                    st.session_state.target_language = new_list_lang
                    reset_progress()
                    st.success(f"🎉 Lyckades! Listan '{new_list_title}' med {len(parsed_words)} glosor har lagts till i biblioteket och valts automatiskt!")
                    st.rerun()
                else:
                    st.warning("Hittade inga giltiga glosor att läsa in. Ladda upp en fil eller klistra in fritext.")
                    
            st.markdown("---")
            st.markdown("### 🗑️ Ta bort gloslistor från biblioteket")
            
            # Visa listor och låt läraren rensa
            all_lists = list(st.session_state.library.keys())
            for list_name in all_lists:
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"📁 {list_name} ({st.session_state.library[list_name]['language']}) — **{len(st.session_state.library[list_name]['words'])}** ord")
                with col2:
                    # Hindra radering om det bara finns en lista kvar
                    if len(all_lists) > 1:
                        if st.button("Radera", key=f"del_list_{list_name}"):
                            st.session_state.library.pop(list_name)
                            # Om den raderade listan var den aktiva, ladda en annan
                            if st.session_state.current_list_name == list_name:
                                new_active = list(st.session_state.library.keys())[0]
                                st.session_state.current_list_name = new_active
                                st.session_state.words = st.session_state.library[new_active]["words"].copy()
                                st.session_state.target_language = st.session_state.library[new_active]["language"]
                                reset_progress()
                            st.toast(f"Listan '{list_name}' togs bort från biblioteket!")
                            st.rerun()
                    else:
                        st.caption("Kan ej raderas")
