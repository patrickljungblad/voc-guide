"""Övningsspel: Para ihop och Blixtrunda, samt en tydlig meny över alla sätt att öva.

Spelen och extraövningarna flyttar inte orden mellan lådorna. Det gör bara den vanliga
repetitionen (Kör igång), så att lådorna visar vad eleven faktiskt minns över tid.
"""
import random
import time
from html import escape
import streamlit as st
from core.answers import normalize
from core.trainer import options_for
from ui.style import html
from ui.visuals import steps, symbol, word_card

MATCH_SIZE = 6
BLITZ_SECONDS = 60


def _fields():
    """Vilket språk som visas och vilket som efterfrågas, enligt vald träningsriktning."""
    forward = st.session_state.direction == "forward"
    return ("svenska", "accepted_answers") if forward else ("accepted_answers", "svenska")


def _text(word, field):
    value = word[field]
    return value[0] if isinstance(value, list) else value


# ---------- Menyn ----------

def modes(vocab):
    language = vocab["language"].lower()
    return [
        ("match", "pairs", "Para ihop", f"Hitta paren: svenska och {language} ord som hör ihop.", "Spela"),
        ("blitz", "bolt", "Blixtrunda", f"Så många rätt du hinner på {BLITZ_SECONDS} sekunder.", "Spela"),
        ("quiz", "choice", "Flerval", "Välj rätt översättning bland fyra alternativ.", "Öva"),
        ("write", "pen", "Skriv själv", "Skriv ordet utan hjälp. Det som fastnar bäst!", "Öva"),
        ("cards", "cards", "Ordkort", "Säg svaret högt och vänd kortet för att se om du hade rätt.", "Öva"),
    ]


def practice_menu(vocab, key_prefix="menu"):
    """Alla sätt att öva på samma ställe, så att eleverna hittar spelen och de andra lägena."""
    html('<div class="section-title" id="fler-satt">Fler sätt att öva</div>')
    st.caption("Spelen och extraövningarna är för att nöta och ha kul. Orden flyttar bara mellan lådorna när du kör den vanliga repetitionen.")
    items = modes(vocab)
    for offset in range(0, len(items), 3):
        columns = st.columns(3, gap="small")
        for column, (mode, icon, title, text, verb) in zip(columns, items[offset:offset + 3]):
            with column, st.container(key=f"mode_{key_prefix}_{mode}"):
                html(f'<div class="mode-card"><span class="mode-icon">{symbol(icon)}</span>'
                     f'<p class="mode-title">{escape(title)}</p><p class="mode-text">{escape(text)}</p></div>')
                if st.button(f"{verb}: {title}", key=f"{key_prefix}_{mode}", use_container_width=True):
                    open_mode(vocab, mode)


def open_mode(vocab, mode):
    st.session_state.session = None
    st.session_state.pop("match", None)
    st.session_state.pop("blitz", None)
    if mode in ("match", "blitz"):
        st.session_state.view = mode
        st.rerun()
    # Ordkort, flerval och skriv är extra övning i den vanliga övningsvyn.
    from ui.training import start
    st.session_state.view = "training"
    start(vocab, mode, extra=True)


def back_to_list(label="Tillbaka till listan", key="game_back"):
    if st.button(label, icon=":material/arrow_back:", key=key):
        st.session_state.pop("match", None)
        st.session_state.pop("blitz", None)
        st.session_state.view = "list"
        st.rerun()


# ---------- Para ihop ----------

def _new_match(vocab):
    ids = [w["id"] for w in vocab["words"]]
    random.shuffle(ids)
    state = {"list": vocab["id"], "direction": st.session_state.direction, "queue": ids, "done": [],
             "selected": None, "misses": 0, "wrong": False, "started": time.time(), "finished_at": None}
    _next_board(state)
    return state


def _next_board(state):
    board = state["queue"][:MATCH_SIZE]
    state["queue"] = state["queue"][MATCH_SIZE:]
    state["board"] = board
    state["left"] = random.sample(board, len(board))
    state["right"] = random.sample(board, len(board))
    state["matched"] = []
    state["selected"] = None


def _pick(state, side, word_id):
    selected = state["selected"]
    state["wrong"] = False
    if selected is None or selected[0] == side:
        state["selected"] = (side, word_id)
        return
    state["selected"] = None
    if selected[1] == word_id:
        state["matched"].append(word_id)
        state["done"].append(word_id)
        if len(state["matched"]) == len(state["board"]):
            if state["queue"]:
                _next_board(state)
            else:
                state["finished_at"] = time.time()
    else:
        state["misses"] += 1
        state["wrong"] = True


def _duration(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 60}:{seconds % 60:02d}" if seconds >= 60 else f"{seconds} sekunder"


def match_game(vocab):
    state = st.session_state.get("match")
    if not state or state["list"] != vocab["id"] or state["direction"] != st.session_state.direction:
        state = st.session_state.match = _new_match(vocab)
    words = {w["id"]: w for w in vocab["words"]}
    shown, asked = _fields()
    total = len(vocab["words"])

    with st.container(key="game_header"):
        left, middle, right = st.columns([1.3, 5, 1.6], vertical_alignment="center")
        with left:
            back_to_list("Avsluta", "match_quit")
        with middle:
            steps(len(state["done"]), total)
        with right:
            html(f'<div class="streak-wrap"><span class="chip off">{len(state["done"])} av {total} par</span></div>')

    if state["finished_at"]:
        seconds = state["finished_at"] - state["started"]
        misses = state["misses"]
        html(f'''<div class="completion">{symbol("check")}<h2>Alla par hittade!</h2>
        <div class="score">{total} par på {_duration(seconds)}</div>
        <p>{"Inga missar alls – imponerande!" if not misses else f"{misses} {'miss' if misses == 1 else 'missar'} på vägen."}
        Spela igen och försök slå din tid.</p></div>''')
        if not misses and not state.get("celebrated"):
            state["celebrated"] = True
            st.balloons()
        again, back = st.columns(2)
        with again, st.container(key="cta"):
            if st.button("Spela igen", type="primary", use_container_width=True, key="match_again"):
                st.session_state.match = _new_match(vocab)
                st.rerun()
        with back:
            back_to_list(key="match_back_done")
        return

    html('<p class="game-hint">Klicka på ett ord till vänster och sedan på det som hör ihop med det till höger.</p>')
    if state["wrong"]:
        st.caption("Inte ett par – försök igen!")
    with st.container(key="match_board"):
        columns = st.columns(2, gap="medium")
        for column, side, order, field in ((columns[0], "L", state["left"], shown), (columns[1], "R", state["right"], asked)):
            with column:
                for word_id in order:
                    matched = word_id in state["matched"]
                    selected = state["selected"] == (side, word_id)
                    label = ("✓ " if matched else "") + _text(words[word_id], field)
                    if st.button(label, key=f"match_{side}_{word_id}", disabled=matched, use_container_width=True,
                                 type="primary" if selected else "secondary"):
                        _pick(state, side, word_id)
                        st.rerun()


# ---------- Blixtrunda ----------

def _blitz_word(vocab, state):
    choices = [w for w in vocab["words"] if w["id"] != state.get("word")] or vocab["words"]
    word = random.choice(choices)
    state["word"] = word["id"]
    state["options"] = options_for(word, vocab["words"], st.session_state.direction)


def _new_blitz(vocab):
    state = {"list": vocab["id"], "direction": st.session_state.direction, "started": time.time(),
             "score": 0, "answered": 0, "last": None, "missed": [], "over": False, "word": None}
    _blitz_word(vocab, state)
    return state


def _time_left(state):
    return max(0.0, BLITZ_SECONDS - (time.time() - state["started"]))


@st.fragment(run_every=1)
def _blitz_timer():
    """Klockan uppdateras varje sekund utan att resten av sidan laddas om."""
    state = st.session_state.get("blitz")
    if not state:
        return
    left = _time_left(state)
    if left <= 0 and not state["over"]:
        state["over"] = True
        st.rerun(scope="app")
    html(f'<div class="blitz-timer" role="timer" aria-label="{int(left)} sekunder kvar">'
         f'<div class="blitz-bar"><i style="width:{left / BLITZ_SECONDS * 100:.1f}%"></i></div>'
         f'<span>{int(left)} s</span></div>')


def blitz_game(vocab):
    state = st.session_state.get("blitz")
    if not state or state["list"] != vocab["id"] or state["direction"] != st.session_state.direction:
        state = st.session_state.blitz = _new_blitz(vocab)
    if not state["over"] and _time_left(state) <= 0:
        state["over"] = True
    words = {w["id"]: w for w in vocab["words"]}
    shown, asked = _fields()
    destination = vocab["language"] if st.session_state.direction == "forward" else "svenska"

    with st.container(key="game_header"):
        left, middle, right = st.columns([1.3, 5, 1.6], vertical_alignment="center")
        with left:
            back_to_list("Avsluta", "blitz_quit")
        with middle:
            if state["over"]:
                html('<div class="blitz-timer"><div class="blitz-bar"><i style="width:0%"></i></div><span>0 s</span></div>')
            else:
                _blitz_timer()
        with right:
            html(f'<div class="streak-wrap"><span class="chip on">{state["score"]} rätt</span></div>')

    if state["over"]:
        records = st.session_state.setdefault("blitz_records", {})
        best = records.get(vocab["id"], 0)
        new_record = state["score"] > best
        if new_record:
            records[vocab["id"]] = state["score"]
        record_line = ("Nytt rekord!" if new_record and best else f"Ditt rekord: {max(best, state['score'])} rätt.")
        html(f'''<div class="completion">{symbol("bolt")}<h2>Tiden är ute!</h2>
        <div class="score">{state["score"]} rätt av {state["answered"]}</div>
        <p>{record_line} Kan du slå det?</p></div>''')
        if new_record and state["score"] and not state.get("celebrated"):
            state["celebrated"] = True
            st.balloons()
        if state["missed"]:
            missed = [words[i] for i in dict.fromkeys(state["missed"]) if i in words]
            rows = "".join(f"<tr><td>{escape(_text(w, shown))}</td><td>{escape(_text(w, asked))}</td></tr>" for w in missed)
            html(f'<p class="game-hint">Ord att titta lite extra på:</p><table class="word-list"><tbody>{rows}</tbody></table>')
        again, back = st.columns(2)
        with again, st.container(key="cta"):
            if st.button("Spela igen", type="primary", use_container_width=True, key="blitz_again"):
                st.session_state.blitz = _new_blitz(vocab)
                st.rerun()
        with back:
            back_to_list(key="blitz_back_done")
        return

    last = state["last"]
    if last:
        html(f'<p class="blitz-last {"ok" if last["correct"] else "miss"}">'
             + ("Rätt!" if last["correct"] else f'Rätt svar var: <b>{escape(last["answer"])}</b>') + "</p>")
    word = words[state["word"]]
    word_card(_text(word, shown), destination)
    correct = {normalize(x) for x in (word[asked] if isinstance(word[asked], list) else [word[asked]])}
    if asked == "svenska":
        correct |= {normalize(x) for x in word.get("swedish_answers", [])}
    with st.container(key="blitz_options"):
        grid = st.columns(2, gap="small")
        for index, option in enumerate(state["options"]):
            with grid[index % 2]:
                if st.button(option, key=f"blitz_{state['answered']}_{index}", use_container_width=True):
                    if _time_left(state) <= 0:
                        state["over"] = True
                    else:
                        right = normalize(option) in correct
                        state["answered"] += 1
                        state["score"] += right
                        state["last"] = {"correct": right, "answer": _text(word, asked)}
                        if not right:
                            state["missed"].append(word["id"])
                        _blitz_word(vocab, state)
                    st.rerun()
