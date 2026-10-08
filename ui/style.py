import base64
from pathlib import Path
import streamlit as st


def html(markup):
    # Indrag i HTML ska inte bli kodblock i Markdown.
    st.markdown("\n".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def apply_style():
    logo = base64.b64encode(Path(__file__).with_name("glosflow-logo.svg").read_bytes()).decode("ascii")
    html('''<style>
    :root {--gf-ink:#173b4c; --gf-muted:#536977; --gf-teal:#05846f; --gf-line:#dce7ed;}
    [data-testid="stAppViewContainer"] {background:radial-gradient(ellipse at 90% 0%,#e4f4f1 0,transparent 42%),#f5f8fb;}
    [data-testid="stHeader"] {background:rgba(245,248,251,.94);}
    .block-container {max-width:1080px; padding-top:4rem; padding-bottom:3rem;}
    h1,h2,h3,.hero-title {font-family:system-ui,sans-serif; color:var(--gf-ink); letter-spacing:-.045em;}
    h3 {font-size:1.4rem; overflow-wrap:anywhere;}
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {color:var(--gf-muted)!important;}
    .brand {max-width:320px;}
    .brand img {display:block; width:100%; height:auto;}
    .st-key-app_header {margin-bottom:12px;}
    .st-key-app_header [data-testid="stHorizontalBlock"] {flex-wrap:nowrap!important; align-items:center;}
    .st-key-app_header [data-testid="stColumn"] {min-width:0!important;}
    .st-key-account_nav [data-testid="stButton"] {display:flex; justify-content:flex-end;}
    .st-key-account_nav button {border-radius:999px; background:rgba(255,255,255,.8); font-size:14px;}
    .st-key-account_nav button p {white-space:nowrap;}
    .st-key-practice_nav [data-testid="stHorizontalBlock"] {flex-wrap:nowrap!important;}
    .st-key-practice_nav [data-testid="stColumn"] {min-width:0!important;}
    .account-label {text-align:right; font-size:13px; color:var(--gf-muted); overflow-wrap:anywhere;}
    .hero {display:flex; align-items:center; justify-content:space-between; gap:24px; padding:32px 36px;
        border:1px solid #d1e8e5; border-radius:28px; background:linear-gradient(120deg,#edf5ff,#eaf7f2);
        box-shadow:0 12px 36px rgba(32,83,98,.035); margin:8px 0 12px; overflow:hidden;}
    .eyebrow {font-size:11px; font-weight:750; letter-spacing:.14em; text-transform:uppercase; color:#356d78; margin-bottom:10px;}
    .hero-title {font-size:clamp(30px,4.1vw,44px); font-weight:780; line-height:1.14; margin:0 0 14px!important; padding:0!important;}
    .hero-title span {color:#05846f;}
    .hero-copy {font-size:15px; color:#425e6c; line-height:1.6; max-width:430px; margin:0;}
    .hero-art {flex:0 0 240px; width:240px; height:190px;}
    .section-intro {display:flex; align-items:center; justify-content:space-between; gap:14px; margin:8px 0;}
    .section-intro h2 {font-size:22px; font-weight:730; letter-spacing:-.035em; margin:0!important; padding:0!important;}
    .section-intro span {color:var(--gf-muted); font-size:13px;}
    [class*="st-key-vocab_"] {padding:16px; border:1px solid #e0e9ef; border-radius:24px; background:white;
        box-shadow:0 7px 24px rgba(24,57,76,.045); transition:transform .18s ease,box-shadow .18s ease; height:100%;}
    [class*="st-key-vocab_"]:hover {transform:translateY(-3px); box-shadow:0 12px 30px rgba(24,57,76,.085);}
    [class*="st-key-vocab_"] h3 {font-size:21px; line-height:1.3; margin-top:0; min-height:2.6em;}
    .card-art {height:120px; position:relative; display:flex; align-items:center; justify-content:center; border-radius:16px; overflow:hidden;}
    .palette-blue {background:linear-gradient(120deg,#eaf1ff,#e6f4fa); color:#2467ba;}
    .palette-mint {background:linear-gradient(120deg,#e0f4ea,#e5f5f2); color:#07896e;}
    .palette-sky {background:linear-gradient(120deg,#e4f3ff,#e2f5f2); color:#167c9a;}
    .card-art:before,.card-art:after {content:''; position:absolute; width:140px; height:140px; border:1px solid currentColor;
        border-radius:50%; opacity:.09; right:-30px; top:15px;}
    .card-art:after {width:200px; height:200px; right:-60px; top:-15px;}
    .card-art svg {width:124px; height:100px; position:relative; z-index:1;}
    .language-pill {position:absolute; top:12px; left:12px; padding:4px 9px; background:rgba(255,255,255,.8);
        border-radius:999px; font-size:10px; font-weight:750; letter-spacing:.07em; color:#315a70; max-width:70%; overflow-wrap:anywhere;}
    .card-status {font-size:13px; color:var(--gf-muted); margin:2px 0 8px;}
    .card-status b {color:#087760; font-weight:650;}
    .mini-meter {display:flex; height:5px; background:#eaf0f4; border-radius:9px; overflow:hidden; margin:5px 0 6px;}
    .mini-meter i {display:block; height:100%;}
    .mini-meter .red {background:#e69892;} .mini-meter .amber {background:#e3bf6c;} .mini-meter .green {background:#52b796;}
    [class*="st-key-vocab_"] button {border:1px solid #d9e9e6; background:#f0f8f6; color:#076653; border-radius:12px; font-weight:650;}
    button[kind="primary"], [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
        background:linear-gradient(110deg,#167ba2,#05876e); border-color:transparent; border-radius:13px; font-weight:650;
        min-height:46px; box-shadow:0 5px 14px rgba(5,132,111,.12);}
    button[kind="primary"]:hover {filter:brightness(1.06);}
    button:focus-visible {outline:3px solid #2563eb!important; outline-offset:3px;}
    [data-testid="stExpander"] {border:1px solid var(--gf-line); border-radius:15px; background:rgba(255,255,255,.65);}
    [data-testid="stForm"] {border:0; padding:0;}
    [data-testid="stTextInput"] input {border-radius:12px;}
    .list-heading {display:flex; align-items:center; gap:14px; margin:6px 0 12px;}
    .list-heading-icon {width:56px; height:56px; flex:0 0 56px; border-radius:16px; background:#e5f4f0;
        color:#05846f; display:flex; align-items:center; justify-content:center;}
    .list-heading-icon svg {width:28px; height:28px;}
    .list-meta {color:var(--gf-muted); font-size:13px; margin:0;}
    .st-key-list_launch, .st-key-practice_start, .st-key-practice_modes {background:white; border:1px solid var(--gf-line); border-radius:22px; padding:22px; box-shadow:0 5px 20px rgba(24,57,76,.025);}
    .st-key-list_launch {background:linear-gradient(120deg,#f0f8ff,#eef9f4);}
    .start-title {font-size:25px; font-weight:750; color:var(--gf-ink); letter-spacing:-.035em; line-height:1.25; margin:0 0 6px;}
    .start-copy {font-size:14px; color:var(--gf-muted); line-height:1.6; margin:0;}
    .boxes {display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:10px 0 16px;}
    .box {padding:16px; border-radius:17px; background:#fff; border:1px solid var(--gf-line); color:#496271;}
    .box b {display:block; font-size:27px; font-weight:750; color:var(--gf-ink); line-height:1.4;}
    .box span {font-size:12px;} .box strong {font-size:12px; font-weight:650;}
    .box.red {background:#fff7f6; border-color:#efdfdc;} .box.amber {background:#fffaf0; border-color:#eee4ca;}
    .box.green {background:#edf9f3; border-color:#d0eadd;}
    .exercise-meta {display:flex; align-items:center; justify-content:space-between; gap:10px; font-size:13px; color:var(--gf-muted); margin:8px 0;}
    .mode-pill {padding:5px 10px; border-radius:999px; background:#e2f2ed; color:#06745e; font-size:10px; font-weight:750; letter-spacing:.1em;}
    .word-card {position:relative; padding:34px 24px; border:1px solid #cfe1eb; border-radius:25px;
        background:linear-gradient(130deg,#edf5ff,#f0faf5); color:var(--gf-ink); text-align:center; margin:8px 0 12px;
        box-shadow:0 12px 30px rgba(37,99,130,.035); overflow:hidden;}
    .word-card:after {content:''; position:absolute; width:190px; height:190px; border:1px solid #a3d3cd;
        border-radius:50%; right:-110px; bottom:-100px; opacity:.45; pointer-events:none;}
    .word-card .eyebrow {margin-bottom:16px;}
    .word-card .prompt {font-size:clamp(28px,4vw,46px); font-weight:760; letter-spacing:-.03em; line-height:1.2; overflow-wrap:anywhere;}
    .word-card.is-flipped {animation:card-reveal .25s ease-out; background:linear-gradient(130deg,#e8f8f1,#f7fcfa);}
    .st-key-answer_quiz [data-testid="stRadio"] [role="radiogroup"] {display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px;}
    .st-key-answer_quiz [data-testid="stRadio"] label[data-baseweb="radio"] {margin:0; padding:14px; border:1px solid #d7e4eb; border-radius:14px;
        background:#fff; transition:background .15s,border-color .15s; width:100%; box-sizing:border-box; min-height:56px; overflow-wrap:anywhere;}
    .st-key-answer_quiz [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {background:#e8f6f0; border-color:#36a68d; box-shadow:0 0 0 1px #36a68d;}
    .st-key-answer_quiz [data-testid="stRadio"] label[data-baseweb="radio"]:focus-within {outline:3px solid #2563eb; outline-offset:2px;}
    .st-key-answer_write {background:white; border:1px solid var(--gf-line); padding:20px; border-radius:20px;}
    .st-key-practice_modes [role="radiogroup"] {gap:12px;}
    .st-key-practice_modes label[data-baseweb="radio"] {background:#f5f9fb; border:1px solid #dce7ed; padding:10px 14px; border-radius:12px;}
    .feedback-signal {display:flex; align-items:center; gap:10px; font-size:13px; font-weight:650; color:#067760; margin:5px 0;}
    .feedback-signal svg {width:32px; height:32px; animation:feedback-pop .3s ease-out;}
    .feedback-signal.near {color:#91641b;} .feedback-signal.wrong {color:#356779;}
    .completion {padding:28px; border:1px solid #cce8dd; border-radius:26px; background:linear-gradient(120deg,#eaf8f0,#edf5ff); text-align:center; margin:12px 0;}
    .completion svg {width:64px; height:64px; color:#05846f; animation:feedback-pop .35s ease-out;}
    .completion h2 {font-size:31px; margin:12px 0 8px; padding:0!important;}
    .completion p {color:var(--gf-muted); margin:0; font-size:15px; line-height:1.6;}
    [data-testid="stProgress"] [role="progressbar"] {border-radius:999px;}
    .sr-only {position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0;}
    @keyframes feedback-pop {from {transform:scale(.8); opacity:.4;} to {transform:scale(1); opacity:1;}}
    @keyframes card-reveal {from {transform:translateY(4px); opacity:.7;} to {transform:translateY(0); opacity:1;}}
    @media(max-width:640px) {
        .block-container {padding-top:3.6rem; padding-left:18px; padding-right:18px;}
        .brand {max-width:260px;} .st-key-app_header {margin-bottom:4px;}
        .hero {padding:24px; gap:0; border-radius:22px;} .hero-art {display:none;}
        .hero-title {font-size:32px;} .hero-copy {font-size:14px;}
        .section-intro {align-items:flex-start;} .section-intro h2 {font-size:21px;}
        [class*="st-key-vocab_"] h3 {min-height:0;}
        .boxes {gap:7px;} .box {padding:12px 9px;} .box strong {font-size:11px;} .box span {font-size:11px;}
        .word-card {padding:27px 18px; border-radius:21px;}
        .st-key-answer_quiz [data-testid="stRadio"] [role="radiogroup"] {grid-template-columns:1fr; gap:8px;}
        .st-key-answer_quiz [data-testid="stRadio"] label[data-baseweb="radio"] {padding:12px; min-height:48px;}
        .st-key-practice_start,.st-key-practice_modes,.st-key-list_launch {padding:18px;}
    }
    @media(prefers-reduced-motion:reduce) {*,*:before,*:after {animation:none!important; transition:none!important; scroll-behavior:auto!important;}}
    </style>''')
    html(f'<div class="brand"><img src="data:image/svg+xml;base64,{logo}" width="420" height="100" alt="GlosFlow – Öva. Minns. Se dina framsteg."></div>')


def boxes(counts):
    html(f'''<div class="boxes">
    <div class="box red"><strong>Ska övas</strong><b>{counts[1]}</b><span>Lite oftare</span></div>
    <div class="box amber"><strong>På väg</strong><b>{counts[2]}</b><span>Efter 3 dagar</span></div>
    <div class="box green"><strong>Kan bra</strong><b>{counts[3]}</b><span>Efter 7 dagar</span></div>
    </div>''')
