"""Små vektorillustrationer och tydliga statusytor, utan externa bildanrop."""
from html import escape
from ui.style import html


def symbol(name="book"):
    paths = {
        "book": '<path d="M4 6c5-2 8-1 12 2v20c-4-3-7-4-12-2V6Zm24 0c-5-2-8-1-12 2v20c4-3 7-4 12-2V6Z"/>',
        "check": '<circle cx="16" cy="16" r="13"/><path d="m10 16 4 4 8-9"/>',
        "retry": '<path d="M26 13a11 11 0 1 0 0 8M26 4v9h-9"/>',
        "spark": '<path d="m16 3 4 9 9 4-9 4-4 9-4-9-9-4 9-4 4-9Z"/>',
    }
    return f'<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'


def library_hero():
    html('''<div class="hero"><div>
    <div class="eyebrow">Små omgångar. Nya möjligheter.</div>
    <h1 class="hero-title">Vad vill du<br><span>lära dig idag?</span></h1>
    <p class="hero-copy">Välj en gloslista, lyssna och hitta ditt flow.<br>En liten stund idag gör plats för nästa steg.</p>
    </div><svg class="hero-art" viewBox="0 0 260 200" aria-hidden="true">
    <circle cx="139" cy="97" r="86" fill="#d8eee7"/>
    <circle cx="139" cy="97" r="98" fill="none" stroke="#bfded5" stroke-dasharray="3 8"/>
    <g transform="rotate(-12 120 95)"><rect x="37" y="49" width="133" height="112" rx="17" fill="#d0e5f0"/><rect x="32" y="42" width="133" height="112" rx="17" fill="#fff" stroke="#c5dce7"/>
    <text x="52" y="70" font-family="Arial,sans-serif" font-size="11" font-weight="700" fill="#3b749a">ETT ORD I TAGET</text>
    <text x="53" y="115" font-family="Arial,sans-serif" font-size="32" font-weight="700" fill="#26649a">hola</text></g>
    <g transform="rotate(9 174 134)"><rect x="112" y="94" width="118" height="81" rx="15" fill="#079575"/>
    <text x="132" y="145" font-family="Arial,sans-serif" font-size="31" font-weight="700" fill="#fff">hej</text></g>
    <circle cx="213" cy="48" r="22" fill="#fff" stroke="#d0e7dc"/><path d="m203 49 6 6 13-15" fill="none" stroke="#078d70" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M39 160c-16-1-22 6-22 18 13 0 23-5 22-18Z" fill="#67bba2"/>
    </svg></div>''')


def card_art(index, language):
    palette = ("blue", "mint", "sky")[index % 3]
    html(f'''<div class="card-art palette-{palette}"><span class="language-pill">{escape(language.upper())}</span>
    <svg viewBox="0 0 140 110" fill="none" aria-hidden="true">
    <rect x="42" y="21" width="64" height="76" rx="12" fill="currentColor" opacity=".16" transform="rotate(12 74 59)"/>
    <rect x="32" y="12" width="64" height="76" rx="12" fill="white" stroke="currentColor" stroke-opacity=".25" transform="rotate(-8 64 50)"/>
    <text x="45" y="59" font-family="Arial,sans-serif" font-size="29" font-weight="700" fill="currentColor">Aa</text>
    <path d="M95 61c12 0 19 7 19 17s-7 17-19 17H83l-9 7 1-13c-4-3-6-7-6-11 0-10 10-17 26-17Z" fill="currentColor"/>
    <path d="m85 78 6 5 11-12" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    </svg></div>''')


def mini_progress(c, total):
    label = f"{c[1]} Ska övas, {c[2]} På väg, {c[3]} Kan bra"
    html(f'''<div class="mini-meter" role="img" aria-label="{label}">
    <i class="red" style="width:{c[1] / total * 100:.2f}%"></i>
    <i class="amber" style="width:{c[2] / total * 100:.2f}%"></i>
    <i class="green" style="width:{c[3] / total * 100:.2f}%"></i></div>''')


def word_card(prompt, destination, flipped=False):
    html(f'''<div class="word-card{' is-flipped' if flipped else ''}">
    <div class="eyebrow">{'Svaret' if flipped else 'Översätt till ' + escape(destination)}</div>
    <div class="prompt">{escape(prompt)}</div></div>''')


def feedback_signal(result):
    name, label = {"correct": ("check", "Ett steg vidare"), "near": ("spark", "Du är nära"),
                   "wrong": ("retry", "Vi övar vidare")}[result]
    html(f'<div class="feedback-signal {result}">{symbol(name)}<span>{label}</span></div>')


def completion(practiced, needs_work):
    follow_up = f"{needs_work} av dem ligger i Ska övas. Du får fler chanser att träna dem." if needs_work else "Nästa repetition hjälper dig att minnas längre."
    html(f'''<div class="completion">{symbol('check')}<h2>Snyggt jobbat.</h2>
    <p>Du har tränat <strong>{practiced} olika glosor</strong> i den här omgången.<br>{follow_up}</p></div>''')
