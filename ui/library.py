import time
import streamlit as st
from core.leitner import counts, due_words


def library(lists):
    st.subheader("Vad vill du träna på?")
    categories = sorted({v["category"] for v in lists})
    category = st.selectbox("Kategori", categories)
    for vocab in lists:
        if vocab["category"] != category:
            continue
        c = counts(vocab, st.session_state.progress, st.session_state.direction)
        due = len(due_words(vocab, st.session_state.progress, st.session_state.direction, time.time(), limit=300))
        with st.container(border=True):
            st.subheader(vocab["name"])
            st.caption(f"{vocab['language']} · {len(vocab['words'])} glosor · {due} att repetera nu")
            st.write(f"🔴 {c[1]} Ska övas · 🟡 {c[2]} På väg · 🟢 {c[3]} Kan bra")
            if st.button("Öppna listan", key=f"open_{vocab['id']}", use_container_width=True):
                st.session_state.list_id = vocab["id"]
                st.session_state.session = None
                st.rerun()
