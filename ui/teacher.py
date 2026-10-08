from copy import deepcopy
import json
from uuid import uuid4
import streamlit as st
from core.leitner import counts
from core.migration import migrate_legacy
from data.vocabulary import parse_words, validate_lists
from services.database import ServiceError
from ui.navigation import share_list
from ui.themes import THEMES
from ui.visuals import card_art
from ui.print_quiz import print_quiz_panel
from ui.speech_admin import speech_panel


def teacher(db, lists):
    st.subheader("Lärarpanel")
    st.caption("Gloslistorna är synliga för alla som kommer åt appen. Elevkonton och framsteg visas bara efter inloggning.")
    token = st.session_state.user["token"]
    tab_lists, tab_students, tab_print, tab_audio = st.tabs(["Gloslistor", "Elever och framsteg", "Glosförhör", "Röster och ljud"])
    with tab_print:
        print_quiz_panel(lists)
    with tab_audio:
        speech_panel(db, token, lists)
    with tab_lists:
        with st.expander("Skapa gloslista"):
            with st.form("create_list"):
                name = st.text_input("Listans namn", max_chars=160)
                category = st.text_input("Kurs", "Egna listor", max_chars=160)
                language = st.text_input("Språk", "Spanska", max_chars=160)
                theme = st.selectbox("Temabild", ["auto", *THEMES], format_func=lambda t: "Automatisk – utifrån glosorna" if t == "auto" else THEMES[t], key="create_theme")
                st.caption("Klistra in två kolumner från ett kalkylblad: svenska och målspråk. Alternativa svar avskiljs med |. En tredje kolumn kan innehålla ett minnestips.")
                text = st.text_area("Glosor", placeholder="hund\tperro\ndator\tcomputadora|ordenador", height=180)
                submit = st.form_submit_button("Spara ny lista", type="primary")
            if submit:
                try:
                    new_list = {"id": uuid4().hex, "name": name.strip(), "category": category.strip(),
                                "language": language.strip(), "words": parse_words(text), "theme": theme}
                    changed = validate_lists(lists + [new_list])
                    db.save_lists(token, changed)
                    st.session_state.lists = changed
                    st.success("Listan är sparad och finns nu i elevernas bibliotek.")
                    st.rerun()
                except (ServiceError, ValueError) as error:
                    st.error(str(error))
        selected = st.selectbox("Ändra en lista", [v["id"] for v in lists],
                                format_func=lambda i: next(v["name"] for v in lists if v["id"] == i))
        vocab = next(v for v in lists if v["id"] == selected)
        card_art(0, vocab["language"], vocab)
        share_list(vocab)
        with st.form("edit_" + selected):
            new_name = st.text_input("Namn", vocab["name"], max_chars=160)
            new_category = st.text_input("Kurs", vocab["category"], max_chars=160)
            new_language = st.text_input("Språk", vocab["language"], max_chars=160)
            theme_options = ["auto", *THEMES]
            new_theme = st.selectbox("Temabild", theme_options, index=theme_options.index(vocab.get("theme", "auto")) if vocab.get("theme", "auto") in theme_options else 0,
                                     format_func=lambda t: "Automatisk – utifrån glosorna" if t == "auto" else THEMES[t], key="edit_theme_" + selected)
            rows = [{"id": w["id"], "Svenska": "|".join(w["swedish_answers"]),
                     "Målspråk": "|".join(w["accepted_answers"]), "Minnestips": w.get("memory_tip", "")} for w in vocab["words"]]
            st.caption("Flera godkända svar: använd | mellan alternativen. Behåll ordets betydelse när du ändrar en befintlig rad; skapa en ny rad för en ny glosa.")
            edited = st.data_editor(rows, num_rows="dynamic", column_config={"id": None}, disabled=["id"], use_container_width=True, key="editor_" + selected)
            submit = st.form_submit_button("Spara ändringar", type="primary")
        if submit:
            try:
                changed_list = deepcopy(vocab)
                changed_list.update(name=new_name.strip(), category=new_category.strip(), language=new_language.strip(), theme=new_theme)
                old_words = {w["id"]: w for w in vocab["words"]}
                changed_words = []
                for row in edited:
                    wid = row.get("id") or uuid4().hex
                    word = deepcopy(old_words.get(wid, {"id": wid}))
                    sv = row.get("Svenska") or ""
                    target = row.get("Målspråk") or ""
                    word.update(svenska=sv.replace("|", ", "), swedish_answers=[x.strip() for x in sv.split("|")],
                                accepted_answers=[x.strip() for x in target.split("|")], memory_tip=row.get("Minnestips") or "")
                    changed_words.append(word)
                changed_list["words"] = changed_words
                changed = [changed_list if v["id"] == selected else v for v in lists]
                validate_lists(changed)
                db.save_lists(token, changed)
                st.session_state.lists = changed
                st.success("Ändringarna är sparade. Ordens ID och elevframsteg bevaras.")
            except (ServiceError, ValueError) as error:
                st.error(str(error))
        st.download_button("Exportera glosbiblioteket", json.dumps(st.session_state.lists, ensure_ascii=False, indent=2), "glosbibliotek.json", "application/json")
        with st.expander("Importera glosbibliotek från JSON"):
            upload = st.file_uploader("Bibliotek med stabila list- och ord-ID", type=["json"], key="library_import")
            if upload and st.button("Lägg till eller uppdatera importerade listor"):
                try:
                    incoming = validate_lists(json.load(upload))
                    merged = {v["id"]: v for v in lists}
                    merged.update({v["id"]: v for v in incoming})
                    changed = validate_lists(list(merged.values()))
                    db.save_lists(token, changed)
                    st.session_state.lists = changed
                    st.rerun()
                except (ServiceError, ValueError) as error:
                    st.error(str(error))
    with tab_students:
        with st.expander("Skapa elevkonto"):
            with st.form("create_student", clear_on_submit=True):
                name = st.text_input("Elevens namn", max_chars=100)
                group = st.text_input("Klass", max_chars=100)
                pin = st.text_input("Ny PIN-kod (4 siffror)", type="password", max_chars=4)
                submit = st.form_submit_button("Skapa konto", type="primary")
            if submit:
                try:
                    db.create_user(token, name, group, pin)
                    st.success("Elevkontot är skapat.")
                except ServiceError as error:
                    st.error(str(error))
        try:
            students = db.students(token)
        except ServiceError as error:
            st.error(str(error))
            return
        if not students:
            st.info("Skapa ett elevkonto för att komma igång.")
            return
        selected_list = st.selectbox("Visa framsteg för", [v["id"] for v in lists], format_func=lambda i: next(v["name"] for v in lists if v["id"] == i))
        shown = next(v for v in lists if v["id"] == selected_list)
        rows = []
        for student in students:
            boxes = counts(shown, student["progress"], "forward")
            rows.append({"Namn": student["name"], "Klass": student["group"], "Ska övas": boxes[1], "På väg": boxes[2], "Kan bra": boxes[3]})
        st.caption("Svenska till målspråk · lådorna beskriver övning, inte ett betyg.")
        st.dataframe(rows, hide_index=True, use_container_width=True)
        st.download_button("Säkerhetskopia av elevframsteg", json.dumps(students, ensure_ascii=False, indent=2), "elevframsteg.json", "application/json")
        with st.expander("Flytta framsteg från gamla versionen"):
            st.write("Välj elev och ladda upp elevens gamla leitner-dictionary som JSON. Konton behöver skapas på nytt; den gamla backendkoden ingick inte i originalet.")
            selected_student = st.selectbox("Elev", [s["id"] for s in students], format_func=lambda i: next(s["group"] + " · " + s["name"] for s in students if s["id"] == i))
            upload = st.file_uploader("Gammal progression", type=["json"], key="legacy_import")
            if upload and st.button("Importera elevens gamla lådor"):
                try:
                    legacy = json.load(upload)
                    if not isinstance(legacy, dict):
                        raise ValueError("Filen ska innehålla en dictionary med gamla lådnycklar.")
                    migrated, missing = migrate_legacy(legacy.get("leitner", legacy), lists)
                    if not migrated:
                        raise ValueError("Inga matchande glosor hittades.")
                    student = next(s for s in students if s["id"] == selected_student)
                    merged = {**migrated, **student["progress"]}
                    db.import_progress(token, student["id"], merged, student["revision"])
                    st.success(f"{len(migrated)} lådor matchades. Befintliga nya framsteg bevarades.")
                    if missing:
                        st.warning(f"{len(missing)} gamla nycklar matchade inte biblioteket. Behåll originalfilen.")
                except (ServiceError, ValueError, TypeError) as error:
                    st.error(str(error))
