import secrets
import streamlit as st
from services.print_quiz import quiz_versions, quiz_pdf


def print_quiz_panel(lists):
    st.subheader("Skapa glosförhör")
    st.caption("Vanliga översättningsförhör med svarsrader. Facit laddas ner separat.")
    selected = st.selectbox("Gloslista till förhöret", [v["id"] for v in lists],
                            format_func=lambda i: next(v["category"] + " · " + v["name"] for v in lists if v["id"] == i), key="print_list")
    vocab = next(v for v in lists if v["id"] == selected)
    direction = st.radio("Språkriktning för förhöret", ["forward", "reverse"],
                         format_func=lambda d: "Svenska → " + vocab["language"] if d == "forward" else vocab["language"] + " → Svenska", key="print_direction")
    selection = st.radio("Vilka glosor?", ["Alla glosor", "Slumpmässigt urval", "Välj glosor själv"], key="print_selection")
    ids = [w["id"] for w in vocab["words"]]
    amount = len(ids)
    if selection == "Slumpmässigt urval":
        amount = st.number_input("Antal glosor", min_value=1, max_value=len(ids), value=min(10, len(ids)), key="print_count_" + selected)
    elif selection == "Välj glosor själv":
        ids = st.multiselect("Markera glosorna", ids, format_func=lambda i: next(w["svenska"] + " — " + w["accepted_answers"][0] for w in vocab["words"] if w["id"] == i), key="print_words_" + selected)
        amount = len(ids)
    shuffled = st.checkbox("Blanda ordningen", value=True, key="print_shuffle")
    two = st.checkbox("Skapa A- och B-version", key="print_ab")
    st.caption("A och B innehåller samma glosor i olika ordning. Skriv ut i A4 med skala 100 %." if two else "Skriv ut i A4 med skala 100 %.")
    signature = (repr(vocab), direction, selection, tuple(ids), amount, shuffled, two)
    if st.button("Skapa PDF", type="primary", disabled=not ids or (two and amount < 2), key="print_generate"):
        chosen = secrets.SystemRandom().sample(ids, int(amount)) if selection == "Slumpmässigt urval" else ids
        versions = quiz_versions(vocab, chosen, shuffled, two, seed=secrets.randbits(64))
        st.session_state.print_result = (signature, quiz_pdf(vocab, versions, direction), quiz_pdf(vocab, versions, direction, answers=True))
    result = st.session_state.get("print_result")
    if result and result[0] == signature:
        st.success("Förhöret och facit är klara.")
        left, right = st.columns(2)
        with left:
            st.download_button("Ladda ner glosförhör", result[1], "GlosFlow-glosforhor.pdf", "application/pdf", key="download_quiz")
        with right:
            st.download_button("Ladda ner facit", result[2], "GlosFlow-facit.pdf", "application/pdf", key="download_answers")
