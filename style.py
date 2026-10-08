import streamlit as st


def apply_style():
    markup = '''<style>
    .block-container {max-width: 1040px; padding-top: 5rem;}
    .brand {display:flex; gap:12px; align-items:center; margin-bottom:20px;}
    .brand-mark {background:linear-gradient(135deg,#2563eb,#059669); color:white;
        border-radius:14px; padding:8px 17px; font-size:28px; font-weight:800;}
    .brand-name {font-size:32px; font-weight:800; color:#164e63;}
    .brand-note {font-size:14px; color:#475569;}
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
    </style>
    <div class="brand"><div class="brand-mark">G</div><div>
    <div class="brand-name">GlosFlow</div><div class="brand-note">Öva. Minns. Se dina framsteg.</div></div></div>'''
    st.markdown("\n".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def boxes(counts):
    st.markdown(f'''<div class="boxes">
    <div class="box red">🔴 Ska övas<b>{counts[1]}</b>Ofta</div>
    <div class="box amber">🟡 På väg<b>{counts[2]}</b>Efter 3 dagar</div>
    <div class="box green">🟢 Kan bra<b>{counts[3]}</b>Efter 7 dagar</div>
    </div>''', unsafe_allow_html=True)
