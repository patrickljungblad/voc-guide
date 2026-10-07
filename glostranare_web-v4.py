"""Start: streamlit run glostranare_web-v4.py"""
import streamlit as st
from data.vocabulary import builtin_lists, validate_lists
from services.config import database
from services.database import ServiceError, SessionExpired
from ui.style import apply_style
from ui.login import login
from ui.library import library
from ui.training import training
from ui.teacher import teacher

st.set_page_config(page_title="GlosFlow – öva och minns", page_icon="🌱", layout="centered", initial_sidebar_state="collapsed")
apply_style()

for name, default in {"user": None, "progress": {}, "revision": 0, "list_id": None,
                      "session": None, "direction": "forward", "pending": None,
                      "save_error": None, "lists": None}.items():
    if name not in st.session_state:
        st.session_state[name] = default
try:
    db = database()
except ServiceError as error:
    st.error(str(error))
    st.stop()

if st.session_state.user is None:
    login(db)
    st.stop()

user = st.session_state.user
st.sidebar.write(f"**{user['name']}**")
if user["role"] == "guest":
    st.sidebar.caption("Gästläge · framsteg sparas bara under besöket")
if st.sidebar.button("Logga ut", disabled=bool(st.session_state.pending)):
    try:
        if user.get("token"):
            db.logout(user["token"])
    except SessionExpired:
        st.session_state.clear()
        st.rerun()
    except ServiceError as error:
        st.sidebar.error(str(error))
    else:
        st.session_state.clear()
        st.rerun()

if st.session_state.lists is None:
    try:
        custom = db.get_lists()
        by_id = {v["id"]: v for v in builtin_lists()}
        by_id.update({v["id"]: v for v in custom})
        st.session_state.lists = validate_lists(list(by_id.values()))
    except (ServiceError, ValueError) as error:
        st.error(str(error))
        if st.button("Försök hämta listorna igen"):
            st.rerun()
        st.stop()

lists = st.session_state.lists
if user["role"] == "teacher":
    teacher(db, lists)
    st.stop()

with st.sidebar.expander("Träningsriktning"):
    label = st.selectbox("Översätt från", ["Svenska till målspråk", "Målspråk till svenska"],
                         index=0 if st.session_state.direction == "forward" else 1,
                         disabled=bool(st.session_state.pending))
    direction = "forward" if label == "Svenska till målspråk" else "reverse"
    if direction != st.session_state.direction:
        st.session_state.direction = direction
        st.session_state.session = None
        st.rerun()

if st.session_state.list_id is None:
    library(lists)
else:
    vocab = next((v for v in lists if v["id"] == st.session_state.list_id), None)
    if vocab is None:
        st.session_state.list_id = st.session_state.session = None
        st.rerun()
    training(db, vocab)
