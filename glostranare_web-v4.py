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
from ui.list_page import list_page

st.set_page_config(page_title="GlosFlow – öva och minns", page_icon="🌱", layout="centered", initial_sidebar_state="collapsed")
apply_style()

for name, default in {"user": None, "progress": {}, "revision": 0, "list_id": None,
                      "session": None, "direction": "forward", "pending": None,
                      "save_error": None, "lists": None, "show_login": False,
                      "view": "list", "query_list": None}.items():
    if name not in st.session_state:
        st.session_state[name] = default
try:
    db = database()
except ServiceError as error:
    st.error(str(error))
    st.stop()

requested = st.query_params.get("lista")
if requested != st.session_state.query_list and not st.session_state.pending:
    st.session_state.query_list = requested
    st.session_state.list_id = requested
    st.session_state.session = None
    st.session_state.view = "list"
    st.session_state.show_login = False

if st.session_state.user is None:
    st.session_state.user = {"name": "Gäst", "role": "guest"}

user = st.session_state.user
st.sidebar.write(f"**{user['name']}**")
if user["role"] == "guest":
    st.sidebar.caption("Gästläge · framsteg sparas bara under besöket")
    list_view = st.session_state.list_id is not None and st.session_state.view == "list" and not st.session_state.show_login
    if not list_view and st.button("Logga in för att spara framsteg", disabled=bool(st.session_state.pending)):
        st.session_state.show_login = True
        st.rerun()
    if st.sidebar.button("Elev- eller lärarinloggning"):
        st.session_state.show_login = True
        st.rerun()
else:
    st.sidebar.caption("Dina framsteg sparas på kontot." if user["role"] == "student" else "Lärarkonto")
if user["role"] != "guest" and st.sidebar.button("Logga ut", disabled=bool(st.session_state.pending)):
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

if st.session_state.show_login:
    login(db)
    st.stop()

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
        st.warning("Gloslistan i länken finns inte. Den kan ha tagits bort eller länken kan vara felaktig.")
        from ui.navigation import all_lists
        if st.button("Visa alla gloslistor"):
            all_lists()
        st.stop()
    if st.session_state.view == "training":
        training(db, vocab)
    else:
        list_page(vocab)
