import streamlit as st
from ui.audio import word_table
from ui.navigation import all_lists, share_list


def list_page(vocab):
    back, account = st.columns([1, 2])
    with back:
        if st.button("← Alla gloslistor"):
            all_lists()
    with account:
        if st.session_state.user["role"] == "guest" and st.button("Logga in för att spara framsteg"):
            st.session_state.show_login = True
            st.rerun()
    st.subheader(vocab["name"])
    st.caption(f"{vocab['language']} · {len(vocab['words'])} glosor")
    if st.button("▶ Öva denna lista", type="primary", use_container_width=True):
        st.session_state.view = "training"
        st.session_state.session = None
        st.rerun()
    if st.session_state.user["role"] == "guest":
        st.caption("Öva utan konto. Logga in för att spara mellan besöken.")
    share_list(vocab)
    with st.expander("Sök bland glosorna"):
        query = st.text_input("Sökord", key="search_" + vocab["id"], placeholder="Svenska eller målspråk")
    words = [w for w in vocab["words"] if query.strip().casefold() in
             (w["svenska"] + " " + " ".join(w["accepted_answers"])).casefold()]
    if not words:
        st.info("Inga glosor matchar din sökning.")
        return
    word_table(words, vocab["language"])
