import streamlit as st
from services.database import ServiceError


def login(db):
    st.subheader("Logga in när du vill spara")
    st.write("Logga in för att spara din utveckling till nästa gång.")
    st.caption("Använd kontot du fått av din lärare. Inloggningen hämtar dina sparade framsteg; övning du redan gjort som gäst förs inte över till kontot.")
    student, teacher = st.tabs(["Elev", "Lärare"])
    with student:
        with st.form("student_login"):
            name = st.text_input("Namn", key="login_name", max_chars=100)
            pin = st.text_input("PIN-kod", type="password", max_chars=4)
            submit = st.form_submit_button("Logga in", type="primary", use_container_width=True)
        if submit:
            try:
                user = db.authenticate_student(name, pin)
                saved = db.load_progress(user["token"])
                st.session_state.user = user
                st.session_state.progress = saved["progress"]
                st.session_state.revision = saved["revision"]
                st.session_state.session = None
                st.session_state.show_login = False
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
                st.session_state.session = None
                st.session_state.progress = {}
                st.session_state.show_login = False
                st.rerun()
            except ServiceError as error:
                st.error(str(error))
    st.divider()
    if st.button("Fortsätt utan inloggning", use_container_width=True):
        st.session_state.show_login = False
        st.rerun()
    st.caption("Gästens framsteg finns bara kvar i den här webbsessionen.")
