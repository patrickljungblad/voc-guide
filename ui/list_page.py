import streamlit as st
from ui.audio import READ_ALOUD, word_table
from ui.navigation import all_lists, share_list
from ui.style import html
from ui.visuals import symbol
from ui.themes import theme_for, theme_svg
from html import escape


def list_page(vocab):
    if st.button("Alla listor", icon=":material/arrow_back:"):
        all_lists()
    html(f'<div class="list-heading"><div class="list-heading-icon">{theme_svg(theme_for(vocab))}</div><div><div class="eyebrow">Din gloslista</div><p class="list-meta">{escape(vocab["language"])} · {len(vocab["words"])} glosor</p></div></div>')
    st.subheader(vocab["name"])
    with st.container(key="list_launch"):
        intro = "Lyssna på orden först, eller kör igång direkt." if READ_ALOUD else "Titta igenom orden först, eller kör igång direkt."
        html(f'<p class="start-title">Redo att öva?</p><p class="start-copy">{intro}</p>')
        if st.button("Öva på listan", type="primary", use_container_width=True, icon=":material/arrow_forward:"):
            st.session_state.view = "training"
            st.session_state.session = None
            st.rerun()
        if st.session_state.user["role"] == "guest":
            st.caption("Öva utan konto. Logga in för att spara mellan besöken.")
    left, right = st.columns(2)
    with left:
        share_list(vocab)
    with right, st.expander("Sök bland glosorna"):
        query = st.text_input("Sökord", key="search_" + vocab["id"], placeholder="Svenska eller målspråk")
    words = [w for w in vocab["words"] if query.strip().casefold() in
             (w["svenska"] + " " + " ".join(w["accepted_answers"])).casefold()]
    if not words:
        st.info("Inga glosor matchar din sökning.")
        return
    word_table(words, vocab["language"])
