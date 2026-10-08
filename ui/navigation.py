"""Delbara listadresser och navigation utan att blanda elevdata i länken."""
from urllib.parse import urlencode, urlsplit, urlunsplit
import streamlit as st


def list_url(base_url, list_id):
    parts = urlsplit(base_url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path or "/", urlencode({"lista": list_id}), ""))


def open_list(list_id):
    st.query_params["lista"] = list_id
    st.session_state.query_list = list_id
    st.session_state.list_id = list_id
    st.session_state.session = None
    st.session_state.view = "list"
    st.rerun()


def all_lists():
    if "lista" in st.query_params:
        del st.query_params["lista"]
    st.session_state.query_list = None
    st.session_state.list_id = st.session_state.session = None
    st.session_state.view = "list"
    st.rerun()


def share_list(vocab):
    with st.expander("🔗 Dela gloslistan"):
        st.caption("Kopiera länken till eleverna. De kan se glosorna och öva utan konto.")
        # context.url innehåller bara basadressen, aldrig elevens token eller PIN.
        url = list_url(st.context.url or "", vocab["id"])
        st.code(url, language=None)
        st.caption("Länken fortsätter fungera om du ändrar listans namn.")
