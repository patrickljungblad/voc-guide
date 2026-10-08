from copy import deepcopy
from html import escape
import json
import time
from uuid import uuid4
import streamlit as st
from core.answers import grade
from core.leitner import counts, due_words, initial, key, update, next_review_text
from core.trainer import Session, options_for
from pedagogy.memory_strategies import OWN_TIP_MAX, memory_tip, own_tip
from services.database import Conflict, ServiceError, SessionExpired
from ui.style import BOXES, boxes, html
from ui.visuals import answer_card, chip, completion, memory_title, practice_progress, steps, word_card
from ui.audio import listen
from ui.navigation import all_lists


def persist(db):
    pending = st.session_state.pending
    if not pending:
        return True
    try:
        revision = db.save_progress(st.session_state.user["token"], pending["progress"],
                                    pending["revision"], pending["id"])
        st.session_state.revision = revision
        st.session_state.pending = None
        st.session_state.save_error = None
        return True
    except Conflict as error:
        st.session_state.save_error = ("conflict", str(error))
    except SessionExpired as error:
        st.session_state.save_error = ("auth", str(error))
    except ServiceError as error:
        st.session_state.save_error = ("network", str(error))
    return False


def save(db, operation_id=None, defer=False):
    if st.session_state.user["role"] != "student":
        return True
    st.session_state.pending = {"progress": deepcopy(st.session_state.progress),
                               "revision": st.session_state.revision, "id": operation_id or uuid4().hex}
    if defer:
        return True
    return persist(db)


def pending_notice(db):
    if not st.session_state.pending:
        return
    # En ny sparning är på väg att starta efter att återkopplingen har visats.
    if st.session_state.save_error is None:
        return
    error = st.session_state.save_error
    st.warning(error[1])
    st.download_button("Hämta kopia av dina framsteg", json.dumps(st.session_state.progress, ensure_ascii=False, indent=2),
                       "mina-framsteg.json", "application/json")
    if error[0] == "auth":
        user = st.session_state.user
        with st.form("resume_login"):
            st.caption(f"Bekräfta PIN-koden för {user['name']}. Ditt osparade svar bevaras.")
            pin = st.text_input("PIN-kod igen", type="password", max_chars=4)
            submit = st.form_submit_button("Logga in och spara svaret")
        if submit:
            try:
                renewed = db.authenticate(user["name"], user["group"], pin)
                if renewed["id"] != user["id"]:
                    raise ServiceError("Kontot stämmer inte överens med den här träningen.")
                st.session_state.user = renewed
                persist(db)
                st.rerun()
            except ServiceError as login_error:
                st.error(str(login_error))
    elif error[0] != "conflict":
        if st.button("Försök spara igen", type="primary"):
            persist(db)
            st.rerun()
    else:
        st.caption("Kopian ovan innehåller ditt lokala svar. När du hämtar sparad version ersätts den lokala versionen.")
        confirmed = st.checkbox("Jag vill ersätta den lokala versionen med den sparade")
        if st.button("Hämta sparad version", disabled=not confirmed):
            try:
                stored = db.load_progress(st.session_state.user["token"])
                st.session_state.progress = stored["progress"]
                st.session_state.revision = stored["revision"]
                st.session_state.pending = st.session_state.save_error = st.session_state.session = None
                st.rerun()
            except SessionExpired as error:
                st.session_state.save_error = ("auth", str(error))
                st.rerun()
            except ServiceError as error:
                st.error(str(error))


def start(vocab, mode="auto", extra=False):
    eligible = vocab["words"] if extra else due_words(vocab, st.session_state.progress, st.session_state.direction, time.time())
    st.session_state.session = Session([w["id"] for w in eligible[:10]], mode=mode,
        start_green=counts(vocab, st.session_state.progress, st.session_state.direction)[3])
    st.rerun()


def answer(db, vocab, word, result, mode, canonical, given=None):
    session = st.session_state.session
    if session.feedback is not None or st.session_state.pending:
        return
    now = time.time()
    progress_key = key(vocab["id"], word["id"], st.session_state.direction)
    previous = st.session_state.progress.get(progress_key, initial())
    assisted = session.hints > 0 or session.tip or session.listened or word["id"] in session.exposed
    state = update(previous, result, mode, assisted, now)
    st.session_state.progress[progress_key] = state
    session.answered += 1
    session.correct += result == "correct"
    session.streak = session.streak + 1 if result == "correct" else 0
    session.feedback = {"result": result, "answer": canonical, "old_box": previous["box"],
                        "box": state["box"], "assisted": assisted, "mode": mode, "given": given}
    if result != "correct" or assisted:
        session.retry_later(word["id"], [w["id"] for w in vocab["words"]])
    # Ingen nätverksväntan innan eleven får se rättningen.
    save(db, session.turn_id, defer=True)
    st.rerun()


def word_keys(vocab, word):
    """Nuvarande riktning först, så att elevens senaste knep hittas först."""
    other = "reverse" if st.session_state.direction == "forward" else "forward"
    return [key(vocab["id"], word["id"], st.session_state.direction), key(vocab["id"], word["id"], other)]


def memory_panel(db, vocab, word):
    """Visas efter ett fel eller nästan rätt svar: nu är det läge att lära in ordet."""
    session = st.session_state.session
    keys = word_keys(vocab, word)
    mine = own_tip(st.session_state.progress, keys)
    with st.container(key="memory_panel"):
        memory_title()
        st.markdown(f"**Ditt eget knep:** {mine}" if mine else memory_tip(word))
        with st.form("own_tip_" + session.turn_id, border=False):
            text = st.text_input("Ditt eget knep" if not mine else "Ändra ditt knep", value=mine, max_chars=OWN_TIP_MAX,
                                 placeholder="T.ex. Perro har två r, som en hund som morrar: prrr")
            saved = st.form_submit_button("Spara knepet")
        if saved:
            progress = st.session_state.progress
            for progress_key in keys:
                if progress_key in progress:
                    progress[progress_key].pop("own_tip", None)
            if text.strip():
                progress.setdefault(keys[0], initial())["own_tip"] = text.strip()[:OWN_TIP_MAX]
            save(db, defer=True)
            st.rerun()


def learning_info(vocab):
    st.write("Svarar du rätt utan hjälp flyttar ordet ett steg framåt. Svarar du fel flyttar det ett steg bakåt och kommer tillbaka snart.")
    st.caption("För att nå Kan bra behöver du skriva ordet själv, några dagar senare. Varje översättningsriktning har egna lådor.")


def help_panel(word, canonical, mode, vocab):
    session = st.session_state.session
    with st.expander("Jag behöver en ledtråd", expanded=session.listened or session.tip or session.hints > 0,
                     icon=":material/lightbulb:"):
        st.caption("Ta hjälp när du behöver. Ett ord du fått hjälp med flyttas inte framåt den här gången.")
        columns = st.columns(3 if mode == "write" else 2)
        with columns[0]:
            if st.button("Minnestips", key=session.turn_id + "tip", icon=":material/psychology:", use_container_width=True):
                session.tip = True
                st.rerun()
        with columns[1]:
            if st.button("Lyssna på svaret", key=session.turn_id + "listen", icon=":material/volume_up:", use_container_width=True):
                session.listened = True
                session.exposed.add(word["id"])
                st.rerun()
        if mode == "write":
            with columns[2]:
                if st.button("En bokstav", key=session.turn_id + "hint", icon=":material/spellcheck:", use_container_width=True):
                    session.hints = min(len(canonical), session.hints + 1)
                    st.rerun()
        if session.listened:
            listen(canonical, vocab["language"] if st.session_state.direction == "forward" else "Svenska")
        if session.tip:
            mine = own_tip(st.session_state.progress, word_keys(vocab, word))
            if mine:
                st.info("**Ditt eget knep:** " + mine)
            st.info(memory_tip(word))
        if session.hints:
            st.info("Ledtråd: " + canonical[:session.hints] + "_" * (len(canonical) - session.hints))


def start_page(db, vocab):
    progress, direction, pending = st.session_state.progress, st.session_state.direction, bool(st.session_state.pending)
    with st.container(key="practice_nav"):
        back, overview = st.columns([1, 1])
    with back:
        if st.button("Alla listor", icon=":material/arrow_back:", disabled=pending):
            all_lists()
    with overview:
        if st.button("Se glosorna och lyssna", icon=":material/volume_up:", disabled=pending):
            st.session_state.view = "list"
            st.session_state.session = None
            st.rerun()
    pending_notice(db)
    due = due_words(vocab, progress, direction, time.time(), 300)
    if st.session_state.pop("start_now", False) and due and not pending:
        start(vocab)
    with st.container(key="practice_start"):
        target = vocab["language"] if direction == "forward" else "svenska"
        html(f'<div class="eyebrow">Översätt till {escape(target)} · {len(vocab["words"])} glosor</div>'
             f'<p class="start-title">{escape(vocab["name"])}</p>')
        boxes(counts(vocab, progress, direction))
        if due:
            st.caption(f"{len(due)} glosor väntar · högst 10 per omgång")
            with st.container(key="cta"):
                if st.button("Kör igång", type="primary", use_container_width=True, disabled=pending,
                             icon=":material/arrow_forward:"):
                    start(vocab)
        else:
            next_at = min(progress[key(vocab["id"], w["id"], direction)]["next_review"] for w in vocab["words"])
            st.success("Allt är klart för i dag. Snyggt jobbat!")
            st.caption(f"Nästa repetition {next_review_text(next_at, time.time())}.")
    with st.expander("Öva extra på ditt eget sätt"):
        with st.container(key="practice_modes"):
            mode_label = st.radio("Träningssätt", ["Ordkort", "Quiz", "Skriv"], horizontal=True)
            descriptions = {"Ordkort": "Säg svaret högt och vänd kortet för att jämföra.",
                            "Quiz": "Känn igen rätt översättning bland flera alternativ.",
                            "Skriv": "Skriv översättningen och träna på att plocka fram ordet själv."}
            st.caption(descriptions[mode_label] + " Extra övning flyttar inte orden mellan lådorna.")
            if st.button("Starta extra övning", use_container_width=True, disabled=pending):
                start(vocab, {"Ordkort": "cards", "Quiz": "quiz", "Skriv": "write"}[mode_label], extra=True)
    with st.expander("Hur fungerar lådorna?"):
        learning_info(vocab)
    with st.expander("Nollställ framsteg för den här listan"):
        reset = st.checkbox("Jag vill radera lådorna för båda riktningarna i denna lista")
        if st.button("Nollställ listans framsteg", disabled=not reset or pending):
            st.session_state.progress = {k: v for k, v in progress.items() if not k.startswith(vocab["id"] + ":")}
            save(db)
            st.rerun()


def done_page(vocab, session):
    progress, direction = st.session_state.progress, st.session_state.direction
    pending = bool(st.session_state.pending)
    practiced = set(session.queue[:session.index])
    needs_work = sum(progress.get(key(vocab["id"], wid, direction), initial())["box"] == 1 for wid in practiced)
    completion(session.correct, session.answered, len(practiced), needs_work)
    green = counts(vocab, progress, direction)[3] - session.start_green
    if green > 0:
        st.success(f"{green} fler ord ligger nu i Kan bra.")
    boxes(counts(vocab, progress, direction))
    left, right = st.columns(2)
    with left, st.container(key="cta"):
        if st.button("Tillbaka till listan", type="primary", use_container_width=True, disabled=pending):
            st.session_state.session = None
            st.rerun()
    with right:
        if st.button("Till startsidan", use_container_width=True, disabled=pending):
            all_lists()


def question_header(session):
    pending = bool(st.session_state.pending)
    with st.container(key="practice_header"):
        quit_column, bar, streak_column = st.columns([1.1, 6, 1.5], vertical_alignment="center")
    with quit_column:
        if st.button("Avsluta", icon=":material/close:", disabled=pending):
            all_lists()
    with bar:
        steps(session.index + (1 if session.feedback else 0), len(session.queue))
    with streak_column:
        streak = session.streak
        chip(f"{streak} i rad", "on" if streak >= 2 else "hot" if streak else "off")


def feedback_view(db, vocab, word, prompt, destination):
    session = st.session_state.session
    feedback = session.feedback
    pending = bool(st.session_state.pending)
    result = feedback["result"]
    if result == "correct":
        after = f"{session.streak} rätt i rad – snyggt!" if session.streak >= 2 else ""
    elif result == "near":
        after = "Nästan! Kolla stavningen och accenterna."
    else:
        after = "Ordet kommer tillbaka om en stund."
    answer_card(prompt, feedback["answer"], result, feedback.get("given"), after,
                "Du valde" if feedback["mode"] == "quiz" else "Du skrev")
    progress, direction = st.session_state.progress, st.session_state.direction
    moved = feedback["box"] != feedback["old_box"]
    if result == "correct":
        with st.container(key="feedback_correct"):
            st.success("Rätt!")
            if moved:
                boxes(counts(vocab, progress, direction), highlight=feedback["box"], change="+1")
                if feedback["box"] == 3 and not feedback.get("celebrated"):
                    feedback["celebrated"] = True
                    st.balloons()
            elif feedback["assisted"]:
                st.caption("Bra övning med hjälp. Visa att du minns ordet en annan gång, så flyttar det framåt.")
            elif feedback["mode"] == "cards":
                st.caption("Testa quiz eller skriv för att flytta ordet framåt.")
            next_clicked = st.button("Nästa", type="primary", use_container_width=True, disabled=pending)
    else:
        if moved:
            label = next(name for n, _, name, _ in BOXES if n == feedback["box"])
            st.caption(f"Ordet flyttade ett steg tillbaka, till {label}.")
        memory_panel(db, vocab, word)
        next_clicked = st.button("Nästa", type="primary", use_container_width=True, disabled=pending)
    if next_clicked:
        session.advance()
        st.rerun()
    with st.expander("Lyssna på svaret", icon=":material/volume_up:"):
        listen(feedback["answer"], destination)
    # Återkopplingen skickas till webbläsaren före det långsamma anropet.
    if st.session_state.pending and st.session_state.save_error is None:
        st.caption("Sparar dina framsteg…")
        persist(db)
        st.rerun()


def question_view(db, vocab, word, mode, prompt, destination):
    session = st.session_state.session
    field = "accepted_answers" if st.session_state.direction == "forward" else "swedish_answers"
    canonical = word[field][0]
    word_card(prompt, destination)
    if mode == "write":
        with st.container(key="answer_write"), st.form("write_" + session.turn_id, border=False):
            value = st.text_input("Skriv på " + destination, max_chars=300)
            submit = st.form_submit_button("Kontrollera", type="primary", use_container_width=True)
        if submit:
            if not value.strip():
                st.warning("Skriv ett svar först.")
            else:
                result, matched = grade(value, word[field])
                answer(db, vocab, word, result, mode, matched, given=value.strip())
        help_panel(word, canonical, mode, vocab)
    elif mode == "quiz":
        with st.container(key="answer_quiz"), st.form("quiz_" + session.turn_id, border=False):
            value = st.radio("Välj översättning", session.options, index=None, width="stretch")
            submit = st.form_submit_button("Kontrollera", type="primary", use_container_width=True)
        if submit:
            if value is None:
                st.warning("Välj ett alternativ först.")
            else:
                answer(db, vocab, word, "correct" if value == canonical else "wrong", mode, canonical, given=value)
        help_panel(word, canonical, mode, vocab)
    else:
        st.caption("Säg svaret högt innan du vänder kortet.")
        if not session.flipped:
            if st.button("Vänd kortet", type="primary", use_container_width=True):
                session.flipped = True
                st.rerun()
        else:
            word_card(" / ".join(word[field]), destination, flipped=True)
            with st.expander("Lyssna på ordet", icon=":material/volume_up:"):
                listen(canonical, destination)
            left, right = st.columns(2)
            with left:
                if st.button("Behöver öva", use_container_width=True):
                    answer(db, vocab, word, "wrong", mode, canonical)
            with right:
                if st.button("Jag kunde det", type="primary", use_container_width=True):
                    answer(db, vocab, word, "correct", mode, canonical)


def training(db, vocab):
    session = st.session_state.session
    if session is None:
        start_page(db, vocab)
        return
    if session.done:
        pending_notice(db)
        done_page(vocab, session)
        return
    progress, direction = st.session_state.progress, st.session_state.direction
    word = next(w for w in vocab["words"] if w["id"] == session.current)
    prompt = word["svenska"] if direction == "forward" else " / ".join(word["accepted_answers"])
    destination = vocab["language"] if direction == "forward" else "svenska"
    source = "svenska" if direction == "forward" else vocab["language"]
    box = progress.get(key(vocab["id"], word["id"], direction), initial())["box"]
    mode = session.mode if session.mode != "auto" else ("quiz" if box == 1 else "write")
    if mode == "quiz" and not session.options:
        session.options = options_for(word, vocab["words"], direction)
    if mode == "quiz" and len(session.options) < 2:
        mode = "write"

    question_header(session)
    pending_notice(db)
    with st.container(key="practice_layout"):
        main, side = st.columns([2.3, 1], gap="large")
    with side:
        practice_progress(counts(vocab, progress, direction), source, destination)
    with main:
        if session.feedback:
            feedback_view(db, vocab, word, prompt, destination)
        else:
            question_view(db, vocab, word, mode, prompt, destination)
