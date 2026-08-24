import streamlit as st
import random
import json

# Sätt sidkonfiguration
st.set_page_config(
    page_title="Digitala Glostränaren",
    page_icon="🎓",
    layout="centered"
)

# Pedagogiska förbyggda ordbanker baserade på högfrekventa ord (General Service List & kognatforskning)
PREBUILT_BANKS = {
    "Engelska (Topp 50 vanligaste)": [
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
    ],
    "Spanska (Topp 50 vanligaste)": [
        {"svenska": "tid", "utlandska": "tiempo"},
        {"svenska": "år", "utlandska": "año"},
        {"svenska": "folk", "utlandska": "gente"},
        {"svenska": "sätt", "utlandska": "camino"},
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
}

DEFAULT_WORDS = [
    {"svenska": "hund", "utlandska": "dog"},
    {"svenska": "katt", "utlandska": "cat"},
    {"svenska": "äpple", "utlandska": "apple"},
    {"svenska": "bok", "utlandska": "book"},
    {"svenska": "skola", "utlandska": "school"}
]

# Initiera session state för målspråk
if "target_language" not in st.session_state:
    st.session_state.target_language = "Engelska"

# Initiera session state för ordlista
if "words" not in st.session_state:
    st.session_state.words = DEFAULT_WORDS.copy()

# Spårning av vald ordbank för att upptäcka ändringar
if "current_bank" not in st.session_state:
    st.session_state.current_bank = "(Ingen - Använd egen lista)"

# Initiera session state för spelmekanik
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

# Funktion för att återställa spelet och blanda om ordningen
def reset_progress():
    st.session_state.shuffled_order = list(range(len(st.session_state.words)))
    random.shuffle(st.session_state.shuffled_order)
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.total_answered = 0
    st.session_state.flashcard_flipped = False
    st.session_state.hint_count = 0
    st.session_state.quiz_options = []

# Funktion för jag hämta nuvarande ord baserat på den blandade listan
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

# --- APP DESIGN & GRÄNSSNITT ---
st.title("🎓 Digitala Glostränaren")
st.markdown("Välkommen till elevernas digitala glostränare! Öva i din egen takt med vetenskapligt beprövade metoder för språkinlärning.")

# Sidomeny för inställningar
st.sidebar.header("⚙️ Inställningar")

# NY FUNKTION: Välj en förbyggd ordbank direkt i sidomenyn
st.sidebar.subheader("📦 Förbyggda ordbanker")
selected_bank = st.sidebar.selectbox(
    "Välj en färdig ordlista:",
    ["(Ingen - Använd egen lista)", "Engelska (Topp 50 vanligaste)", "Spanska (Topp 50 vanligaste)"],
    index=0 if st.session_state.current_bank == "(Ingen - Använd egen lista)" else 
          (1 if st.session_state.current_bank == "Engelska (Topp 50 vanligaste)" else 2)
)

# Hantera laddning av ordbank vid val
if selected_bank != st.session_state.current_bank:
    st.session_state.current_bank = selected_bank
    if selected_bank == "Engelska (Topp 50 vanligaste)":
        st.session_state.words = PREBUILT_BANKS["Engelska (Topp 50 vanligaste)"].copy()
        st.session_state.target_language = "Engelska"
    elif selected_bank == "Spanska (Topp 50 vanligaste)":
        st.session_state.words = PREBUILT_BANKS["Spanska (Topp 50 vanligaste)"].copy()
        st.session_state.target_language = "Spanska"
    reset_progress()
    st.rerun()

# Hämta namnet på målspråket från session state
target_lang_name = st.session_state.target_language

# Välj träningsriktning i dropdown (selectbox) med dynamiskt språknamn
direction_label_1 = f"Svenska ➔ {target_lang_name}"
direction_label_2 = f"{target_lang_name} ➔ Svenska"

direction = st.sidebar.selectbox(
    "Välj träningsriktning:",
    (direction_label_1, direction_label_2),
    on_change=reset_progress
)

# Visa statistik
st.sidebar.subheader("📊 Dina framsteg")
st.sidebar.write(f"Ord i listan: **{len(st.session_state.words)}**")
if st.session_state.total_answered > 0:
    pct = int((st.session_state.score / st.session_state.total_answered) * 100)
    st.sidebar.write(f"Rätt svar: **{st.session_state.score}** av **{st.session_state.total_answered}** ({pct}%)")
else:
    st.sidebar.write("Rätt svar: **0**")

if st.sidebar.button("🔄 Nollställ framsteg", use_container_width=True):
    reset_progress()
    st.toast("Framsteg nollställda!")

# Skapa tab-paneler för de olika träningslägena
tab1, tab2, tab3, tab4 = st.tabs([
    "🎴 Flashcards (Se & Öva)", 
    "🎯 Flervalsquiz (Välj rätt)", 
    "✍️ Skrivträning (Stava rätt)", 
    "👩‍🏫 Lärarpanel (Hantera glosor)"
])

# Kontrollera om listan är tom
if not st.session_state.words:
    st.warning("⚠️ Ordlistan är tom! Gå till fliken 'Lärarpanel' för att lägga till glosor.")
else:
    current_word = get_current_word()
    
    # Bestäm källtext och målsvar baserat på vald riktning och dynamiskt språknamn
    if direction == direction_label_1:
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
        st.markdown("Se det markerade ordet, tänk efter vad det betyder, och klicka på kortet för att vända det.")
        
        # Flashcard-design med behållare
        card_container = st.container(border=True)
        with card_container:
            st.markdown("<br>", unsafe_allow_html=True)
            if not st.session_state.flashcard_flipped:
                st.markdown(f"<h1 style='text-align: center; color: #1E3A8A;'>{current_word[prompt_lang].upper()}</h1>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: gray;'>({label_prompt})</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h1 style='text-align: center; color: #10B981;'>{current_word[target_lang].upper()}</h1>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: gray;'>({label_target})</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Vänd kortet", use_container_width=True, type="primary"):
                st.session_state.flashcard_flipped = not st.session_state.flashcard_flipped
                st.rerun()
        with col2:
            if st.button("Nästa kort ➔", use_container_width=True):
                next_word()
                st.rerun()

    # ================= TAB 2: FLERVALSQUIZ =================
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
                # Fyll upp om ordlistan är för kort
                distractors = other_words + ["time", "year", "people", "way"][:3 - len(other_words)]
            
            options = distractors + [correct_ans]
            random.shuffle(options)
            st.session_state.quiz_options = options
            st.session_state.quiz_correct_index = options.index(correct_ans)

        st.markdown(f"Vad betyder: **{current_word[prompt_lang].upper()}**?")
        
        with st.form("quiz_form"):
            selected_option = st.radio("Välj ett alternativ:", st.session_state.quiz_options, index=None)
            submit_quiz = st.form_submit_button("Skicka svar", use_container_width=True)

            if submit_quiz:
                if selected_option is None:
                    st.warning("Vänligen välj ett alternativ först!")
                else:
                    st.session_state.total_answered += 1
                    correct_answer = current_word[target_lang]
                    if selected_option == correct_answer:
                        st.session_state.score += 1
                        st.success(f"🎉 Rätt! **{current_word[prompt_lang].upper()}** betyder **{correct_answer.upper()}**.")
                    else:
                        st.error(f"❌ Fel. Det rätta svaret är **{correct_answer.upper()}**.")

        if st.button("Nästa fråga ➔", key="next_quiz", use_container_width=True):
            next_word()
            st.rerun()

    # ================= TAB 3: SKRIVTRÄNING =================
    with tab3:
        st.subheader("✍️ Skriv och stanna rätt")
        st.markdown("Aktiv återkallning är den mest effektiva metoden för att lära sig glosor utantill.")

        st.markdown(f"Översätt ordet: <h3 style='display:inline;'>{current_word[prompt_lang].upper()}</h3>", unsafe_allow_html=True)
        
        user_input = st.text_input("Skriv din översättning här:", key="write_input", placeholder="Stava noggrant...")

        col1, col2 = st.columns(2)
        with col1:
            check_write = st.button("Rätta mitt svar", use_container_width=True, type="primary")
        with col2:
            hint_btn = st.button("💡 Få en ledtråd", use_container_width=True)

        target_word = current_word[target_lang]
        if hint_btn:
            if st.session_state.hint_count < len(target_word):
                st.session_state.hint_count += 1
            st.rerun()

        if st.session_state.hint_count > 0:
            hint_text = target_word[:st.session_state.hint_count] + "_" * (len(target_word) - st.session_state.hint_count)
            st.info(f"Ledtråd: `{hint_text}` (visar {st.session_state.hint_count} av {len(target_word)} bokstäver)")

        if check_write:
            if not user_input.strip():
                st.warning("Skriv in ett svar först!")
            else:
                st.session_state.total_answered += 1
                correct_answer = current_word[target_lang].strip().lower()
                student_answer = user_input.strip().lower()

                if student_answer == correct_answer:
                    st.session_state.score += 1
                    st.success(f"🎉 Strålande! **{current_word[prompt_lang].upper()}** stavas mycket riktigt **{target_word.upper()}**.")
                else:
                    st.error(f"❌ Tyvärr fel ställt eller fel ord. Det korrekta svaret är **{target_word.upper()}**.")

        if st.button("Nästa ord ➔", key="next_write", use_container_width=True):
            next_word()
            st.rerun()

# ================= TAB 4: LÄRARPANEL & HANDLEDNING =================
with tab4:
    st.subheader("👩‍🏫 Hantera veckans glosor")
    st.markdown("Här kan du ställa in målspråket, klistra in veckans glosor direkt från ditt klassmaterial eller hantera de befintliga orden.")

    st.markdown("### 🌐 Språkinställning")
    new_lang_name = st.text_input(
        "Vilket språk tränar eleverna på just nu?", 
        value=st.session_state.target_language,
        help="Skriv t.ex. Engelska, Spanska, Tyska eller Franska. Appens menyer och knappar uppdateras direkt!"
    )
    if new_lang_name != st.session_state.target_language:
        st.session_state.target_language = new_lang_name
        reset_progress()
        st.toast(f"Målspråk ändrat till: {new_lang_name}!")
        st.rerun()

    st.markdown("---")

    # Sektion för filuppladdning och fritext-import
    st.markdown("### 📥 Ladda upp eller klistra in en ny ordlista")
    st.markdown(f"Välj ett av sätten nedan för att läsa in en ny lista för {target_lang_name}:")

    # Lärare kan ladda upp en TXT- eller JSON-fil
    uploaded_file = st.file_uploader("Ladda upp en ordlista (.txt eller .json)", type=["txt", "json"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".json"):
                parsed_words = json.load(uploaded_file)
                # Validering av JSON-format
                if isinstance(parsed_words, list) and all("svenska" in w and "utlandska" in w for w in parsed_words):
                    if st.button("Spara uppladdad JSON-lista", type="primary", use_container_width=True):
                        st.session_state.words = parsed_words
                        st.session_state.current_bank = "(Ingen - Använd egen lista)"
                        reset_progress()
                        st.success(f"🎉 Lyckades! Importerade {len(parsed_words)} ord från JSON-filen.")
                        st.rerun()
                else:
                    st.error("Felaktigt JSON-format! Filen måste vara en lista med objekt som innehåller fälten 'svenska' och 'utlandska'.")
            
            elif uploaded_file.name.endswith(".txt"):
                string_data = uploaded_file.read().decode("utf-8")
                parsed_words = []
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
                        st.error(f"Kunde inte tolka rad {line_no} i TXT-filen: '{line}'. Kontrollera att orden är delade med bindestreck.")
                        st.stop()
                
                if parsed_words:
                    if st.button("Spara uppladdad TXT-lista", type="primary", use_container_width=True):
                        st.session_state.words = parsed_words
                        st.session_state.current_bank = "(Ingen - Använd egen lista)"
                        reset_progress()
                        st.success(f"🎉 Lyckades! Importerade {len(parsed_words)} ord från TXT-filen.")
                        st.rerun()
        except Exception as e:
            st.error(f"Ett fel uppstod vid inläsning av filen: {str(e)}")

    st.markdown("**Eller klistra in råtext här:**")
    import_text = st.text_area(
        "Klistra in glosor här:", 
        height=120, 
        placeholder=f"svenska - översättning\nord1 - översättning1\nord2 - översättning2"
    )

    if st.button("📥 Importera & Ersätt nuvarande ord (Fritext)", use_container_width=True):
        if not import_text.strip():
            st.warning("Textrutan är tom. Klistra in text innan du importerar.")
        else:
            new_words = []
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
                    sv = parts[0].strip()
                    ut = parts[1].strip()
                    if sv and ut:
                        new_words.append({"svenska": sv, "utlandska": ut})
                else:
                    st.error(f"Kunde inte tolka rad {line_no}: '{line}'. Kontrollera formatet.")
                    st.stop()

            if new_words:
                st.session_state.words = new_words
                st.session_state.current_bank = "(Ingen - Använd egen lista)"
                reset_progress()
                st.success(f"🎉 Lyckades! Importerade **{len(new_words)}** nya ord. Appen är nu uppdaterad!")
                st.rerun()

    st.markdown("---")
    st.markdown("### Aktuell ordlista i appen")
    
    if st.session_state.words:
        for idx, item in enumerate(st.session_state.words):
            col1, col2, col3 = st.columns([4, 4, 1])
            with col1:
                st.write(f"Svenska: **{item['svenska']}**")
            with col2:
                st.write(f"{target_lang_name}: **{item['utlandska']}**")
            with col3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.words.pop(idx)
                    reset_progress()
                    st.toast("Ordet raderades!")
                    st.rerun()
    else:
        st.info("Inga glosor i listan just nu.")

    if st.button(f"⚠️ Återställ till standardordlistan (Svenska-{target_lang_name})", use_container_width=True):
        st.session_state.words = DEFAULT_WORDS.copy()
        st.session_state.current_bank = "(Ingen - Använd egen lista)"
        reset_progress()
        st.success("Återställde till standardordlistan!")
        st.rerun()
