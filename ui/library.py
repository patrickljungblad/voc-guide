"""Startsidan: fortsätt där du slutade, din kurs och alla listor."""
import time
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo
import streamlit as st
from core.leitner import counts, due_words, key
from ui.navigation import open_list, practice_list
from ui.style import box_rows, html
from ui.visuals import meter, symbol

ZONE = ZoneInfo("Europe/Stockholm")


def list_stats(vocab, progress, direction, now):
    states = [progress.get(key(vocab["id"], w["id"], direction), {}) for w in vocab["words"]]
    return {
        "counts": counts(vocab, progress, direction),
        "due": len(due_words(vocab, progress, direction, now, limit=300)),
        "last": max((s.get("last_reviewed") or 0 for s in states), default=0),
        "today": sum(1 for s in states if s.get("last_reviewed")
                     and datetime.fromtimestamp(s["last_reviewed"], ZONE).date() == datetime.now(ZONE).date()),
    }


def choose_course(categories):
    html('<div class="greeting">Hej! Vad ska du öva på?</div>')
    with st.container(key="course_choice"):
        html('<h2>Välj kurs</h2><p class="start-copy">Du kan byta kurs när du vill.</p>')
        choice = st.selectbox("Välj kurs", categories, index=None, placeholder="Klicka här och välj din kurs",
                              label_visibility="collapsed", key="course_select")
    if choice:
        st.session_state.chosen_course = choice
        st.rerun()
    st.caption("Gloslistorna visas när du har valt kurs.")


def continue_card(vocab, stats):
    c, due = stats["counts"], stats["due"]
    eyebrow = "Fortsätt där du slutade" if stats["last"] else "Börja här"
    if not due:
        eyebrow = "Klar för i dag"
    with st.container(key="continue_card"):
        html(f'''<div class="continue"><p class="eyebrow">{eyebrow.upper()}</p>
        <p class="title">{escape(vocab["name"])}</p>{meter(c)}
        <div class="counts"><span>{c[1]} ska övas</span><span>{c[2]} på väg</span><span>{c[3]} kan bra</span></div></div>''')
        if st.button("Kör igång" if due else "Öva extra", key="continue_go", type="primary",
                     use_container_width=True, icon=":material/arrow_forward:"):
            practice_list(vocab["id"], start_now=bool(due))


def course_panel(categories, category, selected, all_stats):
    with st.container(key="course_panel"):
        html("<h2>Din kurs</h2>")
        new = st.selectbox("Välj kurs", categories, index=categories.index(category),
                           label_visibility="collapsed", key="course_select")
        if new != category:
            st.session_state.chosen_course = new
            st.rerun()
        totals = {n: sum(s["counts"][n] for s in all_stats) for n in (1, 2, 3)}
        words = sum(len(v["words"]) for v in selected)
        html(f'<div class="big-number"><b>{totals[3]}</b><span>av {words} ord sitter</span></div>')
        box_rows(totals)


def list_card(vocab, stats):
    total = len(vocab["words"])
    known = stats["counts"][3]
    if stats["due"] and stats["last"]:
        status = f'<span class="due">{stats["due"]} väntar</span>'
    elif stats["last"]:
        status = "<span>Klar för i dag</span>"
    else:
        status = "<span>Ny lista</span>"
    with st.container(key="vocab_" + vocab["id"]):
        html(f'''<h3>{escape(vocab["name"])}</h3><div class="bar" aria-hidden="true"><i style="width:{known / total * 100:.0f}%"></i></div>
        <div class="card-line"><span>{known} av {total} kan bra</span>{status}</div>''')
        if st.button("Öppna listan", key=f"open_{vocab['id']}", use_container_width=True):
            open_list(vocab["id"])


def library(lists):
    categories = sorted({v["category"] for v in lists})
    category = st.session_state.get("chosen_course")
    if category not in categories:
        choose_course(categories)
        return

    progress, direction, now = st.session_state.progress, st.session_state.direction, time.time()
    selected = [v for v in lists if v["category"] == category]
    stats = {v["id"]: list_stats(v, progress, direction, now) for v in selected}
    due = sum(s["due"] for s in stats.values())
    today = sum(s["today"] for s in stats.values())

    user = st.session_state.user
    name = user["name"].split()[0] if user.get("role") == "student" else ""
    hello = f"Hej {escape(name)}!" if name else "Hej!"
    waiting = f"{due} ord väntar." if due else "Allt är klart för i dag."
    chip = f'<span class="chip hot">{symbol("flame")}{today} övade i dag</span>' if today else ""
    html(f'{chip}<div class="greeting">{hello}<br>{waiting}</div>')

    # Senast övade listan med ord som väntar; annars första listan med väntande ord.
    with_due = [v for v in selected if stats[v["id"]]["due"]]
    pool = with_due or selected
    target = max(pool, key=lambda v: (stats[v["id"]]["last"], -selected.index(v)))

    left, right = st.columns([1.9, 1], gap="medium")
    with left:
        continue_card(target, stats[target["id"]])
    with right:
        course_panel(categories, category, selected, list(stats.values()))

    html('<div class="section-title">Alla listor</div>')
    for offset in range(0, len(selected), 3):
        columns = st.columns(3, gap="small")
        for column, vocab in zip(columns, selected[offset:offset + 3]):
            with column:
                list_card(vocab, stats[vocab["id"]])
