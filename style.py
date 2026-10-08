import base64
from pathlib import Path
import streamlit as st


def apply_style():
    logo = base64.b64encode(Path(__file__).with_name("glosflow-logo.svg").read_bytes()).decode("ascii")
    markup = '''<style>
    .block-container {max-width: 1040px; padding-top: 5rem;}
    .brand {margin-bottom:20px; max-width:420px;}
    .brand img {display:block; width:100%; height:auto;}
    .word-card {background:linear-gradient(135deg,#eff6ff,#f0fdfa); color:#164e63;
        padding:36px 24px; border:1px solid #cbd5e1; border-radius:20px;
        text-align:center; margin:20px 0; font-size:32px; font-weight:700; overflow-wrap:anywhere;}
    .boxes {display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:18px 0;}
    .box {padding:16px 8px; border-radius:14px; background:#f8fafc;
        border:1px solid #cbd5e1; text-align:center; color:#334155;}
    .box b {display:block; font-size:30px; color:#0f172a;}
    .box.red {border-bottom:5px solid #dc2626;}
    .box.amber {border-bottom:5px solid #d97706;}
    .box.green {border-bottom:5px solid #059669;}
    @media(max-width:600px) {.box {font-size:13px;} .word-card {font-size:26px; padding:24px 14px;}}
    </style>'''
    # Data-URI fungerar utan en separat webbserver för bildfiler.
    markup += f'<div class="brand"><img src="data:image/svg+xml;base64,{logo}" width="420" height="100" alt="GlosFlow – Öva. Minns. Se dina framsteg."></div>'
    st.markdown("\n".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def boxes(counts):
    st.markdown(f'''<div class="boxes">
    <div class="box red">🔴 Ska övas<b>{counts[1]}</b>Ofta</div>
    <div class="box amber">🟡 På väg<b>{counts[2]}</b>Efter 3 dagar</div>
    <div class="box green">🟢 Kan bra<b>{counts[3]}</b>Efter 7 dagar</div>
    </div>''', unsafe_allow_html=True)
