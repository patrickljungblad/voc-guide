import streamlit as st
import random
import json

# Sätt sidkonfiguration
st.set_page_config(
    page_title="Digitala Glostränaren",
    page_icon="🎓",
    layout="centered"
)

# Standardglosor (Svenska - Engelska)
DEFAULT_WORDS = [
    {"svenska": "hund", "utlandska": "dog"},
    {"svenska": "katt", "utlandska": "cat"},
    {"svenska": "äpple", "utlandska": "apple"},
    {"svenska": "bok", "utlandska": "book"},
    {"svenska": "skola", "utlandska": "school"},
    {"svenska": "lärare", "utlandska": "teacher"},
    {"svenska": "flicka", "utlandska": "girl"},
    {"svenska": "pojke", "utlandska": "boy"},
    {"svenska": "springa", "utlandska": "run"},
    {"svenska": "äta", "utlandska": "eat"}
]

# Initiera session state för målspråk (t.ex. Engelska, Spanska, Tyska)
if "target_language" not in st.session_state:
    st.session_state.target_language = "Engelska"

# Initiera session state för ordlista
if "words" not in st.session_state:
    st.session_state.words = DEFAULT_WORDS.copy()

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

# Funktion för att hämta nuvarande ord baserat på den blandade listan
def get_current_word():
    if not st.session_state.words:
        return None
    idx = st.session_state.shuffled_order[st.session_state.current_index]
    # Hantera om listan krympt efter import
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

# Hämta namnet på målspråket från session state
target_lang_name = st.session_state.target_language

# Sidomeny för inställningar
st.sidebar.header("⚙️ Inställningar")

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
st.sidebar.write(f"Ord kvar i listan: **{len(st.session_state.words)}**")
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
            
            # Vi behöver minst 3 andra ord för att göra 4 alternativ
            if len(other_words) >= 3:
                distractors = random.sample(other_words, 3)
            else:
                # Fyll upp om ordlistan är för kort
                distractors = other_words + ["dog", "cat", "apple", "school"][:3 - len(other_words)]
            
            options = distractors + [correct_ans]
            random.shuffle(options)
            st.session_state.quiz_options = options
            st.session_state.quiz_correct_index = options.index(correct_ans)

        st.markdown(f"Vad betyder: **{current_word[prompt_lang].upper()}**?")
        
        # Form för quiz för att hantera sändning utan automatisk omladdning
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
        
        # Textinmatning
        user_input = st.text_input("Skriv din översättning här:", key="write_input", placeholder="Stava noggrant...")

        col1, col2 = st.columns(2)
        with col1:
            check_write = st.button("Rätta mitt svar", use_container_width=True, type="primary")
        with col2:
            hint_btn = st.button("💡 Få en ledtråd", use_container_width=True)

        # Hantera ledtråd
        target_word = current_word[target_lang]
        if hint_btn:
            if st.session_state.hint_count < len(target_word):
                st.session_state.hint_count += 1
            st.rerun()

        # Visa ledtråd om aktiverad
        if st.session_state.hint_count > 0:
            hint_text = target_word[:st.session_state.hint_count] + "_" * (len(target_word) - st.session_state.hint_count)
            st.info(f"Ledtråd: `{hint_text}` (visar {st.session_state.hint_count} av {len(target_word)} bokstäver)")

        # Rätta skrivet svar
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
    st.markdown("Här kan du ställa in målspråket, ladda upp eller klistra in veckans glosor, samt hantera de befintliga orden.")

    # Sektion för att konfigurera vilket språk man tränar
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

    # Importera ordlista - Välj metod
    st.markdown("### 📥 Importera en ny ordlista")
    
    import_method = st.radio(
        "Välj inmatningsmetod:",
        ("Skriv / Klistra in text", "Ladda upp glosfil (.txt eller .json)"),
        horizontal=True
    )

    if import_method == "Skriv / Klistra in text":
        st.markdown(f"Skriv eller klistra in din gloslista rad för rad. Separera det svenska ordet från översättningen på {target_lang_name} med ett bindestreck (`-`), kolon (`:`) eller likamedtecken (`=`).")
        st.markdown("**Format-exempel:**")
        st.code("hund - dog\nkatt - cat\näpple - apple", language="text")

        import_text = st.text_area(
            "Klistra in glosor här:", 
            height=150, 
            placeholder=f"svenska - översättning\nord1 - översättning1\nord2 - översättning2"
        )

        if st.button("📥 Importera & Ersätt nuvarande ord", type="primary", use_container_width=True):
            if not import_text.strip():
                st.warning("Textrutan är tom. Klistra in text innan du importerar.")
            else:
                new_words = []
                lines = import_text.strip().split("\n")
                for line_no, line in enumerate(lines, 1):
                    if not line.strip():
                        continue
                    # Försök splitta på -, : eller =
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
                    reset_progress()
                    st.success(f"🎉 Lyckades! Importerade **{len(new_words)}** nya ord. Appen är nu uppdaterad och framstegen har återställts!")
                    st.rerun()

    else:
        st.markdown("Ladda upp en textfil (`.txt`) eller en JSON-fil (`.json`) med dina glosor.")
        
        # Flikarna ger exempel på de två filformaten
        ex_tab1, ex_tab2 = st.columns(2)
        with ex_tab1:
            st.markdown("**Exempel på textfil (.txt):**")
            st.code("hund - dog\nkatt - cat\näpple - apple", language="text")
        with ex_tab2:
            st.markdown("**Exempel på JSON-fil (.json):**")
            st.code('[\n  {"svenska": "hund", "utlandska": "dog"},\n  {"svenska": "katt", "utlandska": "cat"}\n]', language="json")

        uploaded_file = st.file_uploader(
            "Välj din glosfil:",
            type=["txt", "json"],
            help="Välj en .txt eller .json fil formaterad enligt exemplen ovan."
        )

        if uploaded_file is not None:
            if st.button("📥 Läs in och ersätt med uppladdad fil", type="primary", use_container_width=True):
                new_words = []
                file_name = uploaded_file.name

                try:
                    # Hantera JSON-fil
                    if file_name.endswith('.json'):
                        content = uploaded_file.read().decode("utf-8")
                        data = json.loads(content)
                        if isinstance(data, list):
                            for idx, item in enumerate(data, 1):
                                if isinstance(item, dict) and "svenska" in item and "utlandska" in item:
                                    new_words.append({
                                        "svenska": str(item["svenska"]).strip(),
                                        "utlandska": str(item["utlandska"]).strip()
                                    })
                                else:
                                    st.error(f"Felaktigt format på objekt nummer {idx} i JSON-filen. Varje objekt måste ha fälten 'svenska' och 'utlandska'.")
                                    st.stop()
                        else:
                            st.error("JSON-filen måste innehålla en lista med ordobjekt.")
                            st.stop()

                    # Hantera TXT-fil
                    elif file_name.endswith('.txt'):
                        content = uploaded_file.read().decode("utf-8")
                        lines = content.strip().split("\n")
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
                                st.error(f"Kunde inte tolka rad {line_no} i filen: '{line}'. Kontrollera att du använder rätt avgränsare.")
                                st.stop()

                    # Om allt gick bra och vi hittade ord
                    if new_words:
                        st.session_state.words = new_words
                        reset_progress()
                        st.success(f"🎉 Lyckades! Importerade **{len(new_words)}** ord från filen **{file_name}**. Appen är uppdaterad!")
                        st.rerun()
                    else:
                        st.warning("Inga ord kunde läsas in från filen. Kontrollera innehållet.")

                except json.JSONDecodeError:
                    st.error("Kunde inte tolka JSON-filen. Kontrollera att den är korrekt formaterad JSON.")
                except Exception as e:
                    st.error(f"Ett fel uppstod vid inläsning av filen: {e}")

    st.markdown("---")
    st.markdown("### Aktuell ordlista i appen")
    
    # Visa och hantera nuvarande ord
    if st.session_state.words:
        for idx, item in enumerate(st.session_state.words):
            col1, col2, col3 = st.columns([4, 4, 1])
            with col1:
                st.write(f"Svenska: **{item['svenska']}**")
            with col2:
                st.write(f"{target_lang_name}: **{item['utlandska']}**")
            with col3:
                # Ta bort knapp för individuella ord
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.words.pop(idx)
                    reset_progress()
                    st.toast("Ordet raderades!")
                    st.rerun()
    else:
        st.info("Inga glosor i listan just nu.")

    if st.button(f"⚠️ Återställ till standardordlistan (Svenska-{target_lang_name})", use_container_width=True):
        st.session_state.words = DEFAULT_WORDS.copy()
        reset_progress()
        st.success("Återställde till standardordlistan!")
        st.rerun()
