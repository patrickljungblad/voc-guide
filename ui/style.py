import base64
from pathlib import Path
import streamlit as st

# Färger och typsnitt från designskissen. Ändra här så följer hela appen med.
INK, MUTED, LINE, BG = "#10302B", "#3E5A54", "#DDE6E2", "#F3F6F4"
BRAND, BRAND_DARK, BRAND_SOFT = "#0B6E58", "#08513F", "#E3F3EE"
CORAL, CORAL_SOFT, CORAL_INK = "#FF6B4A", "#FFE4DC", "#B23A1F"
RED, AMBER, AMBER_SOFT = "#E5674F", "#F2B632", "#FFF6DA"


def html(markup):
    # Indrag i HTML ska inte bli kodblock i Markdown.
    st.markdown("\n".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600;700;800&display=swap');
:root {--ink:INK; --muted:MUTED; --line:LINE; --bg:BG; --brand:BRAND; --brand-dark:BRAND_DARK; --brand-soft:BRAND_SOFT;
    --coral:CORAL; --coral-soft:CORAL_SOFT; --coral-ink:CORAL_INK; --red:RED; --amber:AMBER; --amber-soft:AMBER_SOFT;
    --display:'Bricolage Grotesque', 'Figtree', system-ui, sans-serif;}

/* Grund: typsnitt, bakgrund och Streamlits egna detaljer */
.stApp {font-family:'Figtree', system-ui, sans-serif; color:var(--ink);}
/* Bara textelement får Figtree. Ikoner (t.ex. glödlampan i "Jag behöver en ledtråd") är ett eget ikontypsnitt
   och får aldrig ärva ett vanligt typsnitt, då visas ikonens namn som text i stället för bilden. */
.stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp summary,
.stApp td, .stApp th, .stApp [data-testid="stMarkdownContainer"], .stApp [data-baseweb="select"],
.stApp [data-baseweb="tab"], .stApp [data-testid="stCaptionContainer"] {font-family:'Figtree', system-ui, sans-serif;}
[data-testid="stAppViewContainer"] {background:var(--bg);}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stDecoration"] {display:none;}
.block-container {max-width:1120px; padding-top:3.2rem; padding-bottom:3rem;}
h1, h2, h3, .display {font-family:var(--display)!important; color:var(--ink); letter-spacing:-.03em;}
h1 {font-weight:800!important;} h2, h3 {font-weight:800!important;}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {color:var(--muted)!important;}
a {color:var(--brand);}

/* Sidhuvud */
.st-key-app_header {margin-bottom:6px;}
.st-key-app_header [data-testid="stHorizontalBlock"] {flex-wrap:nowrap!important; align-items:center;}
.st-key-app_header [data-testid="stColumn"] {min-width:0!important;}
.brand {max-width:190px;}
.brand img {display:block; width:100%; height:auto;}
.st-key-account_nav [data-testid="stButton"] {display:flex; justify-content:flex-end;}
.st-key-account_nav button {border-radius:999px; background:#fff; border:1px solid var(--line); font-weight:600; min-height:40px;}
.account {display:flex; justify-content:flex-end; align-items:center; gap:8px; font-weight:600; font-size:14px; overflow-wrap:anywhere;}
.account .initials {width:34px; height:34px; flex:0 0 34px; border-radius:50%; background:#DDEBE6; color:var(--brand);
    display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px;}

/* Knappar: mörkgrön som standard, korall för det viktigaste valet på sidan */
.stApp button {border-radius:14px; font-weight:600;}
button[kind="primary"], [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
    background:var(--brand)!important; border-color:var(--brand)!important; color:#fff!important;
    border-radius:16px!important; font-weight:700!important; min-height:54px; font-size:17px;}
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background:var(--brand-dark)!important; border-color:var(--brand-dark)!important;}
.st-key-cta button, .st-key-continue_card button {background:var(--coral)!important; border-color:var(--coral)!important; color:#fff!important;}
.st-key-cta button:hover, .st-key-continue_card button:hover {background:#F0532F!important; border-color:#F0532F!important;}
.stApp button p {font-weight:inherit; font-size:inherit;}
button:focus-visible {outline:3px solid #2563eb!important; outline-offset:3px;}
[data-testid="stBaseButton-secondary"] {background:#fff; border-color:var(--line);}

/* Paneler, fält och meddelanden */
[data-testid="stExpander"] {border:1px solid var(--line); border-radius:18px; background:#fff;}
[data-testid="stExpander"] summary {font-weight:600;}
[data-testid="stForm"] {border:0; padding:0;}
[data-testid="stTextInput"] input {border-radius:14px; min-height:50px; font-size:17px;}
[data-baseweb="select"] > div {border-radius:14px;}
[data-testid="stAlert"] {border-radius:18px;}
[data-testid="stAlertContentSuccess"] {font-weight:600;}
[data-testid="stProgress"] [role="progressbar"] {border-radius:999px;}

/* Startsidan */
.greeting {font-family:var(--display); font-weight:800; font-size:clamp(32px,4.4vw,48px); line-height:1.05; letter-spacing:-.04em; margin:6px 0 14px; color:var(--ink);}
.chip {display:inline-flex; align-items:center; gap:5px; padding:6px 12px; border-radius:999px; font-weight:700; font-size:14px;}
.chip svg {width:16px; height:16px;}
.chip.hot {background:var(--coral-soft); color:var(--coral-ink);}
.chip.on {background:var(--coral); color:#fff;}
.chip.off {background:#E7EEEB; color:var(--muted);}
.st-key-continue_card {background:var(--brand); color:#fff; border-radius:28px; padding:26px;}
.continue .eyebrow {font-size:13px; font-weight:700; letter-spacing:.05em; color:#BFE6DA; margin:0 0 6px;}
.continue .title {font-family:var(--display); font-size:clamp(22px,2.6vw,30px); font-weight:800; line-height:1.12; margin:0 0 16px; color:#fff;}
.continue .meter {display:flex; height:12px; border-radius:999px; overflow:hidden; background:#0A5D4B; margin-bottom:10px;}
.continue .meter i {display:block; height:100%;}
.continue .meter .red {background:#F49A85;} .continue .meter .amber {background:#F7C948;} .continue .meter .green {background:#7FE0BE;}
.continue .counts {display:flex; flex-wrap:wrap; gap:6px 18px; font-size:15px; color:#DFF3EC; margin-bottom:6px;}
.st-key-course_panel {background:#fff; border-radius:28px; padding:22px;}
.st-key-course_panel h2 {font-size:22px; margin:0; padding:0!important;}
.big-number {display:flex; align-items:baseline; gap:8px; margin:6px 0 10px;}
.big-number b {font-family:var(--display); font-size:44px; font-weight:800; color:var(--brand); line-height:1;}
.big-number span {font-size:15px; color:var(--muted);}
.box-rows {display:flex; flex-direction:column; gap:8px;}
.box-row {display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:14px; font-size:15px;}
.box-row .sq {width:12px; height:12px; border-radius:4px; flex:0 0 12px;}
.box-row .label {flex:1;}
.box-row b {font-family:var(--display); font-weight:800; font-size:20px; font-variant-numeric:tabular-nums;}
.box-row.red {background:#F7F3F2;} .box-row.red .sq {background:var(--red);}
.box-row.amber {background:#FBF6E8;} .box-row.amber .sq {background:var(--amber);}
.box-row.green {background:#EAF4F0;} .box-row.green .sq {background:var(--brand);}
.box-row.hit {box-shadow:inset 0 0 0 2px currentColor; font-weight:700;}
.box-row.red.hit {color:var(--red);} .box-row.amber.hit {color:#C99316;} .box-row.green.hit {color:var(--brand);}
.box-row.hit .label, .box-row.hit b {color:var(--ink);}
.st-key-course_choice {background:#fff; border-radius:28px; padding:26px; border:2px solid #9FD3C3;}
.st-key-course_choice h2 {font-size:26px; margin:0 0 6px; padding:0!important;}
.st-key-course_choice [data-baseweb="select"] > div {min-height:54px; font-size:18px; background:var(--brand-soft); border-color:#7FBFAE;}
.section-title {font-family:var(--display); font-weight:800; font-size:24px; letter-spacing:-.03em; margin:26px 0 10px; color:var(--ink);}
[class*="st-key-vocab_"] {padding:18px; border-radius:22px; background:#fff; height:100%; transition:transform .15s ease, box-shadow .15s ease;}
[class*="st-key-vocab_"]:hover {transform:translateY(-2px); box-shadow:0 10px 26px rgba(16,48,43,.07);}
[class*="st-key-vocab_"] h3 {font-size:18px; line-height:1.3; margin:0 0 10px; padding:0!important; min-height:2.6em;}
[class*="st-key-vocab_"] button {background:var(--brand-soft); border:0; color:var(--brand); font-weight:700;}
.bar {height:6px; border-radius:999px; background:#E7EEEB; overflow:hidden; margin:0 0 10px;}
.bar i {display:block; height:100%; background:var(--brand); border-radius:999px;}
.card-line {display:flex; justify-content:space-between; gap:10px; font-size:14px; color:var(--muted); margin-bottom:10px;}
.card-line .due {font-weight:700; color:var(--coral-ink);}

/* Listans sida och starten på en övning */
.st-key-list_launch, .st-key-practice_start {background:#fff; border-radius:28px; padding:26px;}
.start-title {font-family:var(--display); font-size:clamp(26px,3.2vw,34px); font-weight:800; color:var(--ink); letter-spacing:-.035em; line-height:1.1; margin:0 0 6px;}
.start-copy {font-size:15px; color:var(--muted); line-height:1.6; margin:0;}
.list-heading {display:flex; align-items:center; gap:14px; margin:6px 0 12px;}
.list-heading-icon {width:56px; height:56px; flex:0 0 56px; border-radius:16px; background:var(--brand-soft);
    color:var(--brand); display:flex; align-items:center; justify-content:center;}
.list-heading-icon svg {width:28px; height:28px;}
.eyebrow {font-size:12px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); margin-bottom:6px;}
.list-meta {color:var(--muted); font-size:14px; margin:0;}
.st-key-practice_modes [role="radiogroup"] {gap:10px;}
.st-key-practice_modes label[data-baseweb="radio"] {background:#F5F9F7; border:1px solid var(--line); padding:10px 14px; border-radius:12px;}

.card-art {height:120px; position:relative; display:flex; align-items:center; justify-content:center; border-radius:16px; overflow:hidden; background:var(--brand-soft); color:var(--brand);}
.card-art svg {width:124px; height:100px;}
.language-pill {position:absolute; top:12px; left:12px; padding:4px 9px; background:#fff; border-radius:999px; font-size:10px; font-weight:700; letter-spacing:.07em; color:var(--muted);}

/* Glostabell utan ljud */
.word-list {width:100%; border-collapse:separate; border-spacing:0; background:#fff; border-radius:20px; overflow:hidden; margin-top:12px;}
.word-list th {text-align:left; background:var(--brand-soft); color:var(--brand-dark); padding:14px 18px; font-size:14px;}
.word-list td {padding:14px 18px; border-top:1px solid var(--line); font-size:17px; overflow-wrap:anywhere;}
.word-list td:last-child {font-weight:700;}

/* Lådorna som rutor */
.boxes {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin:12px 0 16px;}
.box {padding:14px; border-radius:18px; background:var(--bg); display:flex; flex-direction:column; gap:2px;}
.box .sq {width:10px; height:10px; border-radius:3px;}
.box b {font-family:var(--display); font-size:28px; font-weight:800; color:var(--ink); line-height:1.25; font-variant-numeric:tabular-nums;}
.box strong {font-size:14px; font-weight:700;} .box span {font-size:12px; color:var(--muted);}
.box.red .sq {background:var(--red);} .box.amber .sq {background:var(--amber);} .box.green .sq {background:var(--brand);}
.box.hit {background:#fff; box-shadow:inset 0 0 0 2px var(--amber); animation:box-arrive .45s ease-out;}
.box.red.hit {box-shadow:inset 0 0 0 2px var(--red);} .box.green.hit {box-shadow:inset 0 0 0 2px var(--brand);}

/* Övningen */
.st-key-practice_header {margin-bottom:6px;}
.st-key-practice_header [data-testid="stHorizontalBlock"] {flex-wrap:nowrap!important; align-items:center;}
.st-key-practice_header [data-testid="stColumn"] {min-width:0!important;}
.st-key-practice_header button {border:0; background:transparent; color:var(--muted);}
.steps {display:grid; gap:5px;}
.steps i {display:block; height:10px; border-radius:5px; background:var(--line);}
.steps i.done {background:var(--brand);}
.streak-wrap {display:flex; justify-content:flex-end;}
.word-card {padding:48px 24px; border-radius:30px; background:#fff; color:var(--ink); text-align:center; margin:4px 0 14px;}
.word-card .eyebrow {margin-bottom:12px;}
.word-card .prompt {font-family:var(--display); font-size:clamp(40px,6vw,68px); font-weight:800; letter-spacing:-.04em; line-height:1.05; overflow-wrap:anywhere;}
.word-card .given {font-size:16px; color:var(--muted); margin-bottom:6px;}
.word-card .given s {text-decoration-thickness:2px;}
.word-card .after {font-size:15px; color:var(--muted); margin-top:10px;}
.word-card.correct .prompt {color:var(--brand);}
.word-card.is-flipped {animation:card-reveal .25s ease-out; background:var(--brand-soft);}
.st-key-answer_quiz [data-testid="stRadio"] > label {display:none;}
.st-key-answer_quiz [data-testid="stRadio"] [role="radiogroup"] {display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px;}
.st-key-answer_quiz [data-testid="stRadio"] label[data-baseweb="radio"] {margin:0; padding:14px; border:2px solid var(--line); border-radius:20px;
    background:#fff; width:100%; box-sizing:border-box; min-height:76px; justify-content:center; align-items:center; overflow-wrap:anywhere; cursor:pointer;}
.st-key-answer_quiz [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {display:none;}
.st-key-answer_quiz [data-testid="stRadio"] label[data-baseweb="radio"] p {font-size:20px; font-weight:700; text-align:center;}
.st-key-answer_quiz [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {background:var(--brand-soft); border-color:var(--brand); color:var(--brand);}
.st-key-answer_quiz [data-testid="stRadio"] label[data-baseweb="radio"]:focus-within {outline:3px solid #2563eb; outline-offset:2px;}
.st-key-answer_write {background:#fff; padding:20px; border-radius:24px;}
.st-key-feedback_correct {background:var(--brand-soft); border-radius:24px; padding:20px;}
.st-key-feedback_correct [data-testid="stAlert"] {background:transparent; padding:0;}
.st-key-feedback_correct [data-testid="stAlertContentSuccess"] p {font-family:var(--display); font-size:26px; font-weight:800; color:var(--brand-dark);}
.st-key-feedback_correct [data-testid="stAlertContentSuccess"] svg, .st-key-feedback_correct [data-testid="stAlertDynamicIcon"] {display:none;}
.st-key-memory_panel {background:var(--amber-soft); border-radius:24px; padding:20px;}
.memory-title {font-family:var(--display); font-weight:800; font-size:21px; color:var(--ink); margin:0 0 6px; display:flex; align-items:center; gap:10px;}
.memory-title .ic {width:36px; height:36px; border-radius:10px; background:var(--amber); display:flex; align-items:center; justify-content:center;}
.memory-title .ic svg {width:20px; height:20px;}
.st-key-memory_panel [data-testid="stTextInput"] input {background:#fff; border:2px solid #E8D193;}
.st-key-memory_panel button {background:var(--ink)!important; color:#fff!important; border:0!important; min-height:44px;}
.practice-progress {background:#fff; border-radius:24px; padding:20px; color:var(--muted);}
.practice-progress .scope {font-size:12px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; margin:0 0 12px;}
.practice-progress .metrics {display:flex; flex-direction:column; gap:8px;}
.practice-progress .metrics span {display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:14px; font-size:15px; color:var(--ink);}
.practice-progress .metrics b {margin-left:auto; font-family:var(--display); font-weight:800; font-size:20px; font-variant-numeric:tabular-nums;}
.practice-progress .dot {display:inline-block; width:12px; height:12px; border-radius:4px; flex-shrink:0;}
.practice-progress .metrics span.r {background:#F7F3F2;} .practice-progress .metrics span.a {background:#FBF6E8;} .practice-progress .metrics span.g {background:#EAF4F0;}
.practice-progress .red {background:var(--red);} .practice-progress .amber {background:var(--amber);} .practice-progress .green {background:var(--brand);}
.practice-progress .rule {font-size:14px; line-height:1.5; margin:12px 0 0;}
.completion {padding:36px 24px; border-radius:30px; background:#fff; text-align:center; margin:8px 0 12px;}
.completion svg {width:64px; height:64px; color:var(--brand); animation:feedback-pop .35s ease-out;}
.completion h2 {font-size:clamp(32px,4vw,44px); margin:10px 0 6px; padding:0!important;}
.completion p {color:var(--muted); margin:0; font-size:16px; line-height:1.6;}
.completion .score {font-family:var(--display); font-size:22px; font-weight:800; color:var(--brand); margin:4px 0 8px;}
.sr-only {position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0;}
@keyframes feedback-pop {from {transform:scale(.8); opacity:.4;} to {transform:scale(1); opacity:1;}}
@keyframes box-arrive {from {transform:translateY(6px) scale(.96);} to {transform:none;}}
@keyframes card-reveal {from {transform:translateY(4px); opacity:.7;} to {transform:translateY(0); opacity:1;}}

/* Mobil */
@media(max-width:640px) {
    .block-container {padding-top:3rem; padding-left:16px; padding-right:16px;}
    .brand {max-width:150px;}
    .st-key-continue_card, .st-key-course_panel, .st-key-course_choice, .st-key-list_launch, .st-key-practice_start {padding:20px; border-radius:24px;}
    .word-card {padding:34px 18px; border-radius:26px;}
    .boxes {gap:7px;} .box {padding:11px 9px;} .box b {font-size:24px;}
    .st-key-answer_quiz [data-testid="stRadio"] label[data-baseweb="radio"] {min-height:66px;}
    .st-key-answer_quiz [data-testid="stRadio"] label[data-baseweb="radio"] p {font-size:18px;}
    /* Lådorna visas som en rad ovanför frågan i stället för i sidopanelen */
    .st-key-practice_layout [data-testid="stHorizontalBlock"] {flex-direction:column;}
    .st-key-practice_layout [data-testid="stColumn"]:last-child {order:-1;}
    .practice-progress {padding:12px 14px; border-radius:18px;}
    .practice-progress .scope {margin-bottom:6px;}
    .practice-progress .metrics {flex-direction:row; flex-wrap:wrap; gap:6px 14px;}
    .practice-progress .metrics span {padding:0; background:transparent!important; font-size:13px; gap:5px;}
    .practice-progress .metrics b {margin-left:2px; font-size:15px;}
    .practice-progress .dot {width:8px; height:8px;}
    .practice-progress .rule {display:none;}
    .st-key-practice_header [data-testid="stColumn"]:first-child button p {display:none;}
    .st-key-practice_header .chip {padding:5px 9px; font-size:13px;}
}
@media(prefers-reduced-motion:reduce) {*,*:before,*:after {animation:none!important; transition:none!important; scroll-behavior:auto!important;}}
"""


def apply_style():
    css = CSS
    for name, value in {"AMBER_SOFT": AMBER_SOFT, "CORAL_SOFT": CORAL_SOFT, "CORAL_INK": CORAL_INK, "BRAND_DARK": BRAND_DARK,
                        "BRAND_SOFT": BRAND_SOFT, "CORAL": CORAL, "AMBER": AMBER, "BRAND": BRAND, "MUTED": MUTED,
                        "LINE": LINE, "INK": INK, "RED": RED, "BG": BG}.items():
        css = css.replace(name, value)
    logo = base64.b64encode(Path(__file__).with_name("glosflow-logo.svg").read_bytes()).decode("ascii")
    html(f"<style>{css}</style>")
    html(f'<div class="brand"><img src="data:image/svg+xml;base64,{logo}" width="430" height="110" alt="GlosFlow"></div>')


BOXES = ((1, "red", "Ska övas", "Övas ofta"), (2, "amber", "På väg", "Var 3:e dag"), (3, "green", "Kan bra", "Var 7:e dag"))


def boxes(counts, highlight=None, change=None):
    """Tre lådor som rutor. `highlight` markerar lådan ordet just hamnade i, `change` är t.ex. "+1"."""
    cells = []
    for n, color, label, hint in BOXES:
        hit = " hit" if n == highlight else ""
        extra = f" {change}" if hit and change else ""
        cells.append(f'<div class="box {color}{hit}"><i class="sq" aria-hidden="true"></i><b>{counts[n]}</b>'
                     f'<strong>{label}{extra}</strong><span>{hint}</span></div>')
    html('<div class="boxes" role="group" aria-label="Dina lådor">' + "".join(cells) + "</div>")


def box_rows(counts, highlight=None, change=None):
    """Lådorna som rader, för sidopaneler."""
    rows = []
    for n, color, label, _ in BOXES:
        hit = " hit" if n == highlight else ""
        extra = f" {change}" if hit and change else ""
        rows.append(f'<div class="box-row {color}{hit}"><i class="sq" aria-hidden="true"></i>'
                    f'<span class="label">{label}{extra}</span><b>{counts[n]}</b></div>')
    html('<div class="box-rows" role="group" aria-label="Lådor">' + "".join(rows) + "</div>")
