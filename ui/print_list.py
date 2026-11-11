"""Knapp för att skriva ut en gloslista som PDF, för både elever och lärare."""
import json
import re
import streamlit as st
from services.print_quiz import word_list_pdf


@st.cache_data(max_entries=50, show_spinner=False)
def _pdf(vocab_json, with_tips):
    # Samma lista ger samma PDF, så den skapas bara en gång och delas av alla.
    return word_list_pdf(json.loads(vocab_json), with_tips)


def filename(vocab):
    name = re.sub(r"[^0-9A-Za-zÅÄÖåäö]+", "-", vocab["name"]).strip("-") or "gloslista"
    return f"GlosFlow-{name}.pdf"


def print_button(vocab, key_prefix="print"):
    with st.container(key=key_prefix + "_list_print"):
        with_tips = st.checkbox("Med minnestips", key=f"{key_prefix}_tips_{vocab['id']}")
        data = _pdf(json.dumps(vocab, ensure_ascii=False, sort_keys=True), with_tips)
        st.download_button("Skriv ut gloslistan", data, filename(vocab), "application/pdf",
                           icon=":material/print:", use_container_width=True, key=f"{key_prefix}_pdf_{vocab['id']}")
        st.caption("Öppna PDF:en och skriv ut den. Vik papperet på mitten för att förhöra dig själv.")
