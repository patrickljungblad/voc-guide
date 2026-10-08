from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo
from html import escape
import json
import time
from uuid import uuid4
import streamlit as st
from core.answers import grade
from core.leitner import counts, due_words, initial, key, update, LABELS
from core.trainer import Session, options_for
from pedagogy.memory_strategies import memory_tip
from services.database import Conflict, ServiceError, SessionExpired
from ui.style import boxes
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
            st.caption(f"Bekräfta PIN-koden för {user['name']} i {user.get('group', '')}. Ditt osparade svar bevaras.")
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


def answer(db, vocab, word, result, mode, canonical):
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
                        "box": state["box"], "assisted": assisted, "mode": mode}
    if result != "correct" or assisted:
        session.retry_later(word["id"], [w["id"] for w in vocab["words"]])
    # Ingen nätverksväntan innan eleven får se rättningen.
    save(db, session.turn_id, defer=True)
    st.rerun()


def training(db, vocab):
    if st.button("← Alla gloslistor", disabled=bool(st.session_state.pending)):
        all_lists()
    if st.button("Se glosorna och lyssna", disabled=bool(st.session_state.pending)):
        st.session_state.view = "list"
        st.session_state.session = None
        st.rerun()
    st.subheader(vocab["name"])
    progress = st.session_state.progress
    direction = st.session_state.direction
    boxes(counts(vocab, progress, direction))
    with st.expander("Så fungerar lådorna"):
        st.write("Svåra ord kommer tillbaka oftare. Ett rätt quiz- eller skrivsvar kan flytta ett ord till På väg. Efter minst tre dagar kan ett skrivsvar utan hjälp flytta det till Kan bra. Gröna ord kontrolleras efter sju dagar. Fel svar flyttar tillbaka ordet till Ska övas.")
        st.caption("Ordkort tränar minnet, men självbedömning flyttar inte ord framåt. Hjälpta och nästan rätta svar ger heller inget avancemang. De två översättningsriktningarna har egna lådor.")
    pending_notice(db)
    session = st.session_state.session
    if session is None:
        due = due_words(vocab, progress, direction, time.time(), 300)
        if due:
            st.write(f"**{len(due)} glosor redo att övas.** En omgång börjar med högst 10 ord.")
            if st.button("▶ Fortsätt träna", type="primary", use_container_width=True, disabled=bool(st.session_state.pending)):
                start(vocab)
        else:
            next_at = min(progress[key(vocab["id"], w["id"], direction)]["next_review"] for w in vocab["words"])
            st.success("Du är klar med dagens planerade repetition. Fint jobbat!")
            st.caption(f"Nästa repetition: {datetime.fromtimestamp(next_at, ZoneInfo('Europe/Stockholm')).strftime('%Y-%m-%d')}.")
        with st.expander("Välj träningssätt själv"):
            mode_label = st.radio("Träningssätt", ["Ordkort", "Quiz", "Skriv"], horizontal=True)
            st.caption("Här kan du öva extra även på ord som inte är redo för repetition. Extra övning förkortar inte väntetiden till gröna lådan.")
            if st.button("Starta extra övning", disabled=bool(st.session_state.pending)):
                start(vocab, {"Ordkort": "cards", "Quiz": "quiz", "Skriv": "write"}[mode_label], extra=True)
        with st.expander("Nollställ framsteg för den här listan"):
            reset = st.checkbox("Jag vill radera lådorna för båda riktningarna i denna lista")
            if st.button("Nollställ listans framsteg", disabled=not reset or bool(st.session_state.pending)):
                st.session_state.progress = {k: v for k, v in progress.items() if not k.startswith(vocab["id"] + ":")}
                save(db)
                st.rerun()
        return
    if session.done:
        st.success(f"Omgången är klar! {session.correct} rätt av {session.answered} svar.")
        green = counts(vocab, progress, direction)[3] - session.start_green
        if green > 0:
            st.write(f"🌱 {green} fler ord ligger nu i Kan bra.")
        st.write("Kom tillbaka när orden är redo att repeteras. Då tränar du på att minnas över tid.")
        if st.button("Till listans översikt", type="primary", disabled=bool(st.session_state.pending)):
            st.session_state.session = None
            st.rerun()
        return
    word = next(w for w in vocab["words"] if w["id"] == session.current)
    field = "accepted_answers" if direction == "forward" else "swedish_answers"
    canonical = word[field][0]
    prompt = word["svenska"] if direction == "forward" else " / ".join(word["accepted_answers"])
    box = progress.get(key(vocab["id"], word["id"], direction), initial())["box"]
    mode = session.mode if session.mode != "auto" else ("quiz" if box == 1 else "write")
    if mode == "quiz" and not session.options:
        session.options = options_for(word, vocab["words"], direction)
    if mode == "quiz" and len(session.options) < 2:
        mode = "write"
    st.caption(f"Ord {session.index + 1} av {len(session.queue)} · {'Skriv' if mode == 'write' else 'Quiz' if mode == 'quiz' else 'Ordkort'} · {session.streak} rätt i rad")
    st.progress(session.index / len(session.queue))
    st.markdown(f'<div class="word-card">{escape(prompt)}</div>', unsafe_allow_html=True)
    if session.feedback:
        feedback = session.feedback
        if feedback["result"] == "correct":
            st.success(f"Rätt! Svaret är: {feedback['answer']}")
            if feedback["box"] > feedback["old_box"]:
                st.write(f"🌱 Ordet flyttades till **{LABELS[feedback['box']]}**!")
            elif feedback["assisted"]:
                st.caption("Bra övning med hjälp. Visa att du minns ordet vid ett senare tillfälle för att flytta det framåt.")
            elif feedback["mode"] == "cards":
                st.caption("Testa ett quiz eller skrivsvar för att flytta ordet framåt.")
        elif feedback["result"] == "near":
            st.warning(f"Nästan rätt! Kontrollera stavningen och accenterna: {feedback['answer']}")
        else:
            st.info(f"Rätt svar är: {feedback['answer']}. Läs, säg ordet högt och försök minnas det till nästa gång.")
        listen(feedback["answer"], vocab["language"] if direction == "forward" else "Svenska")
        if st.button("Nästa ord →", type="primary", use_container_width=True, disabled=bool(st.session_state.pending)):
            session.advance()
            st.rerun()
        # Skicka återkoppling och den tillfälligt spärrade knappen till webbläsaren
        # före det långsamma anropet. Bara en sparning får pågå åt gången.
        if st.session_state.pending and st.session_state.save_error is None:
            st.caption("Sparar dina framsteg…")
            persist(db)
            st.rerun()
        return
    if mode != "cards":
        if st.button("🔊 Lyssna på svaret som hjälp", key=session.turn_id + "listen"):
            session.listened = True
            session.exposed.add(word["id"])
            st.rerun()
        if session.listened:
            st.caption("Svaret visas som hjälp. Ordet flyttas inte framåt av detta svar.")
            listen(canonical, vocab["language"] if direction == "forward" else "Svenska")
        left, right = st.columns(2)
        with left:
            if st.button("🧠 Minnestips", key=session.turn_id + "tip"):
                session.tip = True
                st.rerun()
        with right:
            if mode == "write" and st.button("💡 En bokstav", key=session.turn_id + "hint"):
                session.hints = min(len(canonical), session.hints + 1)
                st.rerun()
        if session.tip:
            st.info(memory_tip(word))
        if session.hints:
            st.info("Bokstavsledtråd: " + canonical[:session.hints] + "_" * (len(canonical) - session.hints))
    if mode == "write":
        with st.form("write_" + session.turn_id):
            value = st.text_input("Skriv på " + (vocab["language"] if direction == "forward" else "svenska"), max_chars=300)
            submit = st.form_submit_button("Rätta mitt svar", type="primary", use_container_width=True)
        if submit:
            if not value.strip():
                st.warning("Skriv ett svar först.")
            else:
                result, matched = grade(value, word[field])
                answer(db, vocab, word, result, mode, matched)
    elif mode == "quiz":
        with st.form("quiz_" + session.turn_id):
            value = st.radio("Välj översättning", session.options, index=None)
            submit = st.form_submit_button("Kontrollera svar", type="primary", use_container_width=True)
        if submit:
            if value is None:
                st.warning("Välj ett alternativ först.")
            else:
                answer(db, vocab, word, "correct" if value == canonical else "wrong", mode, canonical)
    else:
        st.caption("Försök säga svaret innan du vänder kortet.")
        if not session.flipped:
            if st.button("Vänd kortet", type="primary", use_container_width=True):
                session.flipped = True
                st.rerun()
        else:
            st.markdown(f'<div class="word-card">{escape(" / ".join(word[field]))}</div>', unsafe_allow_html=True)
            listen(canonical, vocab["language"] if direction == "forward" else "Svenska")
            left, right = st.columns(2)
            with left:
                if st.button("Behöver öva", use_container_width=True):
                    answer(db, vocab, word, "wrong", mode, canonical)
            with right:
                if st.button("Jag kunde det", use_container_width=True):
                    answer(db, vocab, word, "correct", mode, canonical)
