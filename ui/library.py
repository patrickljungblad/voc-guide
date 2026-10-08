import time
import streamlit as st
from core.leitner import counts, due_words, key
from ui.navigation import open_list
from ui.style import html
from ui.visuals import library_hero, card_art, mini_progress


def library(lists):
    library_hero()
    categories = sorted({v["category"] for v in lists})
    previous = st.session_state.get("chosen_course")
    with st.container(key="course_choice"):
        html('<div class="eyebrow">Steg 1</div><h2>Välj kurs</h2><p>Börja här – välj din kurs.</p>')
        category = st.selectbox("Välj kurs", categories, index=categories.index(previous) if previous in categories else None, placeholder="Klicka här och välj din kurs", label_visibility="collapsed", key="course_select")
    st.session_state.chosen_course = category
    if category is None:
        st.caption("Gloslistorna visas när du har valt kurs.")
        return
    selected = [(i, v) for i, v in enumerate(lists) if v["category"] == category]
    html(f'<div class="section-intro"><h2>Dina gloslistor</h2><span>{len(selected)} listor · i din egen takt</span></div>')
    for offset in range(0, len(selected), 2):
        columns = st.columns(2, gap="medium")
        for column, (index, vocab) in zip(columns, selected[offset:offset + 2]):
            with column, st.container(key="vocab_" + vocab["id"]):
                card_art(index, vocab["language"], vocab)
                st.subheader(vocab["name"])
                c = counts(vocab, st.session_state.progress, st.session_state.direction)
                due = len(due_words(vocab, st.session_state.progress, st.session_state.direction, time.time(), limit=300))
                st.caption(f"{len(vocab['words'])} glosor · {due} redo att öva")
                practiced = any(st.session_state.progress.get(key(vocab["id"], w["id"], st.session_state.direction), {}).get("attempts", 0) for w in vocab["words"])
                if practiced:
                    mini_progress(c, len(vocab["words"]))
                    html(f'<div class="card-status"><b>{c[3]}</b> av {len(vocab["words"])} i Kan bra</div>')
                else:
                    html('<div class="card-status">Din första omgång väntar.</div>')
                if st.button("Öppna listan", key=f"open_{vocab['id']}", use_container_width=True):
                    open_list(vocab["id"])
