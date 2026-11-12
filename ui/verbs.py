"""Verbtränaren: böj spanska verb i presens och perfekt, en person och ett verb i taget, med poäng."""
from html import escape
import streamlit as st
from core.answers import grade
from core.verbs import DEFAULT_GROUPS, GROUPS, PERSON_NAMES, conjugate, make_questions, meaning, rule_hint, table
from ui.style import html
from ui.visuals import steps, symbol

ROUND_SIZES = (10, 20, 30)


def back_home():
    st.session_state.pop("verbs", None)
    st.session_state.view = "list"
    st.session_state.list_id = None
    st.rerun()


def verb_card_link():
    """Kortet på startsidan som leder till Verbtränaren."""
    with st.container(key="verb_card"):
        left, right = st.columns([3, 1.2], vertical_alignment="center")
        with left:
            html(f'<div class="verb-card"><span class="mode-icon">{symbol("pen")}</span><div>'
                 '<p class="mode-title">Verbtränaren</p>'
                 '<p class="mode-text">Öva på att böja spanska verb i presens och perfekt: du får en person och ett verb, och skriver rätt form.</p>'
                 '</div></div>')
        with right:
            if st.button("Öppna Verbtränaren", key="open_verbs", use_container_width=True, icon=":material/arrow_forward:"):
                st.session_state.pop("verbs", None)
                st.session_state.view = "verbs"
                st.rerun()


def setup():
    html('<p class="start-title">Verbtränaren</p>'
         '<p class="start-copy">Du får en person och ett verb, till exempel <b>nosotros · hablar</b>, och skriver rätt form: <b>hablamos</b>.</p>')
    with st.container(key="verb_setup"):
        chosen = []
        for tense, title, example in (("presens", "Presens", "hablo = jag pratar"),
                                      ("perfekt", "Perfekt", "he hablado = jag har pratat")):
            st.markdown(f"**{title}** · *{example}*")
            for group, (label, group_tense, verbs) in GROUPS.items():
                if group_tense == tense and st.checkbox(label, value=group in DEFAULT_GROUPS, key="verbs_group_" + group,
                                                        help=", ".join(f"{v} ({meaning(v)})" for v in verbs)):
                    chosen.append(group)
        st.divider()
        with_vosotros = st.checkbox("Ta med vosotros (ni)", value=True, key="verbs_vosotros")
        count = st.selectbox("Antal frågor", ROUND_SIZES, key="verbs_count")
        with st.container(key="cta"):
            if st.button("Starta", type="primary", use_container_width=True, disabled=not chosen,
                         icon=":material/arrow_forward:"):
                st.session_state.verbs = {"questions": make_questions(chosen, count, with_vosotros), "index": 0,
                                          "results": [], "feedback": None, "settings": (chosen, count, with_vosotros)}
                st.rerun()
        if not chosen:
            st.caption("Välj minst en grupp av verb.")
    with st.expander("Se alla verb och böjningar"):
        for group, (label, tense, verbs) in GROUPS.items():
            st.markdown(f"**{label}** ({tense})")
            rows = "".join(f"<tr><td><b>{escape(v)}</b> ({escape(meaning(v))})</td><td>{escape(', '.join(table(v, tense)))}</td></tr>"
                           for v in verbs)
            html(f'<table class="word-list"><tbody>{rows}</tbody></table>')


def conjugation_table(verb, highlight, tense="presens"):
    rows = "".join(
        f'<tr class="{"hit" if person == highlight else ""}"><td>{escape(PERSON_NAMES[person])}</td><td>{escape(form)}</td></tr>'
        for person, form in enumerate(table(verb, tense)))
    html(f'<table class="word-list verb-table"><tbody>{rows}</tbody></table>')


def question(state):
    total = len(state["questions"])
    item = state["questions"][state["index"]]
    tense = item.get("tense", "presens")
    correct_so_far = sum(r["result"] == "correct" for r in state["results"])
    with st.container(key="verbs_header"):
        middle, right = st.columns([6, 1.4], vertical_alignment="center")
        with middle:
            steps(state["index"] + (1 if state["feedback"] else 0), total)
        with right:
            html(f'<div class="streak-wrap"><span class="chip on">{correct_so_far} rätt</span></div>')

    html(f'''<div class="word-card verb-question"><div class="eyebrow">Fråga {state["index"] + 1} av {total}</div>
    <div class="prompt"><span class="pronoun">{escape(item["pronoun"])}</span> · {escape(item["verb"])}</div>
    <span class="tense-tag {tense}">{tense}</span>
    <div class="after">{escape(meaning(item["verb"]))}</div></div>''')

    feedback = state["feedback"]
    if feedback is None:
        with st.container(key="answer_write"), st.form(f"verb_{state['index']}", border=False):
            value = st.text_input(f"Skriv {item['verb']} i {tense} för {item['pronoun']}", max_chars=60,
                                  placeholder="till exempel: he hablado" if tense == "perfekt" else "")
            submit = st.form_submit_button("Kontrollera", type="primary", use_container_width=True)
        st.caption("Accent: tryck på ´ (bredvid backstegstangenten) och sedan bokstaven, så blir det á, é, í, ó eller ú.")
        if submit:
            if not value.strip():
                st.warning("Skriv ett svar först.")
            else:
                answer = conjugate(item["verb"], item["person"], tense)
                result, _ = grade(value, [answer])
                state["feedback"] = {"result": result, "given": value.strip(), "answer": answer}
                state["results"].append({**item, **state["feedback"]})
                st.rerun()
        return

    if feedback["result"] == "correct":
        with st.container(key="feedback_correct"):
            st.success("Rätt!")
    elif feedback["result"] == "near":
        st.warning(f"Nästan! Rätt form är **{feedback['answer']}** – kolla accenten eller stavningen.")
    else:
        st.error(f"Rätt form är **{feedback['answer']}**. Du skrev {feedback['given']}.")
    if feedback["result"] != "correct":
        st.markdown(rule_hint(item["verb"], tense))
        conjugation_table(item["verb"], item["person"], tense)
    with st.container(key="cta"):
        last = state["index"] + 1 >= total
        if st.button("Se resultatet" if last else "Nästa", type="primary", use_container_width=True, key="verbs_next"):
            state["index"] += 1
            state["feedback"] = None
            st.rerun()


def summary(state):
    results = state["results"]
    total = len(results)
    correct = sum(r["result"] == "correct" for r in results)
    percent = round(correct / total * 100) if total else 0
    message = ("Alla rätt – riktigt starkt!" if correct == total else
               "Bra jobbat! Titta på felen nedan och kör en omgång till." if percent >= 70 else
               "Bra att du övar! Titta på reglerna för verben du missade och prova igen.")
    html(f'''<div class="completion">{symbol("check")}<h2>{correct} av {total} rätt</h2>
    <div class="score">{percent} %</div><p>{message}</p></div>''')
    if correct == total and not state.get("celebrated"):
        state["celebrated"] = True
        st.balloons()
    missed = [r for r in results if r["result"] != "correct"]
    if missed:
        rows = "".join(f"<tr><td>{escape(r['pronoun'])} · {escape(r['verb'])} ({escape(r.get('tense', 'presens'))})</td><td><s>{escape(r['given'])}</s></td>"
                       f"<td><b>{escape(r['answer'])}</b></td></tr>" for r in missed)
        html(f'<p class="game-hint">Det här blev fel:</p><table class="word-list"><thead><tr><th>Fråga</th><th>Du skrev</th>'
             f'<th>Rätt</th></tr></thead><tbody>{rows}</tbody></table>')
    chosen, count, with_vosotros = state["settings"]
    left, middle, right = st.columns(3)
    with left, st.container(key="cta"):
        if st.button("Ny omgång", type="primary", use_container_width=True, key="verbs_again"):
            st.session_state.verbs = {"questions": make_questions(chosen, count, with_vosotros), "index": 0,
                                      "results": [], "feedback": None, "settings": state["settings"]}
            st.rerun()
    with middle:
        if missed and st.button("Öva på mina fel", use_container_width=True, key="verbs_missed"):
            again = [{"verb": r["verb"], "person": r["person"], "pronoun": r["pronoun"], "tense": r.get("tense", "presens")}
                     for r in missed]
            st.session_state.verbs = {"questions": again, "index": 0, "results": [], "feedback": None,
                                      "settings": state["settings"]}
            st.rerun()
    with right:
        if st.button("Ändra inställningar", use_container_width=True, key="verbs_setup"):
            st.session_state.pop("verbs", None)
            st.rerun()


def verb_trainer():
    state = st.session_state.get("verbs")
    playing = state and state["index"] < len(state["questions"])
    # Under en omgång räcker Avsluta; annars leder knappen tillbaka till startsidan.
    if playing:
        if st.button("Avsluta omgången", icon=":material/close:", key="verbs_quit"):
            st.session_state.pop("verbs", None)
            st.rerun()
    elif st.button("Startsidan", icon=":material/arrow_back:", key="verbs_home"):
        back_home()
    if not state:
        setup()
    elif playing:
        question(state)
    else:
        summary(state)
