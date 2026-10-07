import streamlit as st
from services.database import ServiceError


def login(db):
    st.subheader("Välkommen till din glosträning")
    st.write("Logga in för att spara din utveckling till nästa gång.")
    student, teacher = st.tabs(["Elev", "Lärare"])
    with student:
        with st.form("student_login"):
            group = st.text_input("Klass", key="login_group", max_chars=100)
            name = st.text_input("Namn", key="login_name", max_chars=100)
            pin = st.text_input("PIN-kod", type="password", max_chars=4)
            submit = st.form_submit_button("Logga in", type="primary", use_container_width=True)
        if submit:
            try:
                user = db.authenticate(name, group, pin)
                saved = db.load_progress(user["token"])
                st.session_state.user = user
                st.session_state.progress = saved["progress"]
                st.session_state.revision = saved["revision"]
                st.rerun()
            except ServiceError as error:
                st.error(str(error))
    with teacher:
        with st.form("teacher_login"):
            password = st.text_input("Lärarlösenord", type="password")
            submit = st.form_submit_button("Öppna lärarpanelen")
        if submit:
            try:
                st.session_state.user = db.teacher_login(password)
                st.rerun()
            except ServiceError as error:
                st.error(str(error))
    st.divider()
    if st.button("Prova som gäst", use_container_width=True):
        st.session_state.user = {"name": "Gäst", "role": "guest"}
        st.rerun()
    st.caption("Gästens framsteg finns bara kvar i den här webbsessionen.")
