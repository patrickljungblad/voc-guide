"""Små byggblock i HTML: ordkort, stegad förloppsstapel, lådpanel och klar-vy. Inga externa bildanrop."""
from html import escape
from ui.style import html
from ui.themes import theme_for, theme_svg

ICONS = {
    "book": '<path d="M4 6c5-2 8-1 12 2v20c-4-3-7-4-12-2V6Zm24 0c-5-2-8-1-12 2v20c4-3 7-4 12-2V6Z"/>',
    "check": '<circle cx="16" cy="16" r="13"/><path d="m10 16 4 4 8-9"/>',
    "flame": '<path d="M16 4c1.3 5.3 6.7 8 6.7 14.7a6.7 6.7 0 0 1-13.4 0c0-2.7 1.4-4 2.7-5.4 0 2.7 1.3 4 2.7 4 0-5.3-1.4-9.3 1.3-13.3Z"/>',
    "bulb": '<path d="M12 24h8M13.3 28h5.4M16 4a8 8 0 0 0-5.3 14c.9.9 1.3 2 1.3 3.3h8c0-1.3.4-2.4 1.3-3.3A8 8 0 0 0 16 4Z"/>',
}


def symbol(name="book"):
    return (f'<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def card_art(index, language, vocab=None):
    """Temabild för en lista. Används i lärarpanelen."""
    art = theme_svg(theme_for(vocab)) if vocab is not None else symbol("book")
    html(f'<div class="card-art"><span class="language-pill">{escape(language.upper())}</span>{art}</div>')


def chip(text, style="hot", icon="flame"):
    html(f'<div class="streak-wrap"><span class="chip {style}">{symbol(icon)}{escape(text)}</span></div>')


def steps(done, total):
    """Förloppsstapel med ett steg per fråga, som i skissen."""
    total = max(1, total)
    cells = "".join(f'<i class="{"done" if i < done else ""}"></i>' for i in range(total))
    html(f'<div class="steps" style="grid-template-columns:repeat({total},minmax(0,1fr))" role="progressbar" '
         f'aria-valuemin="0" aria-valuemax="{total}" aria-valuenow="{done}" aria-label="{done} av {total} frågor klara">{cells}</div>')


def meter(c):
    total = max(1, sum(c.values()))
    return (f'<div class="meter" aria-hidden="true"><i class="red" style="width:{c[1] / total * 100:.1f}%"></i>'
            f'<i class="amber" style="width:{c[2] / total * 100:.1f}%"></i><i class="green" style="width:{c[3] / total * 100:.1f}%"></i></div>')


def practice_progress(c, source, destination):
    """Listans lådor bredvid frågan. På mobil blir panelen en kompakt rad ovanför frågan."""
    html(f'''<div class="practice-progress" role="group" aria-label="Framsteg i hela gloslistan" aria-live="polite">
    <p class="scope">Hela listan · {escape(source)} → {escape(destination)}</p>
    <div class="metrics"><span class="r"><i class="dot red" aria-hidden="true"></i>Ska övas <b>{c[1]}</b></span>
    <span class="a"><i class="dot amber" aria-hidden="true"></i>På väg <b>{c[2]}</b></span>
    <span class="g"><i class="dot green" aria-hidden="true"></i>Kan bra <b>{c[3]}</b></span></div>
    <p class="rule">Rätt utan hjälp flyttar ordet ett steg framåt. Fel flyttar det ett steg bakåt.</p></div>''')


def word_card(prompt, destination, flipped=False):
    html(f'''<div class="word-card{' is-flipped' if flipped else ''}">
    <div class="eyebrow">{'Svaret' if flipped else 'Översätt till ' + escape(destination)}</div>
    <div class="prompt">{escape(prompt)}</div></div>''')


def answer_card(prompt, answer, result, given=None, after="", given_label="Du skrev"):
    """Ordkortet efter svaret: frågan som liten rubrik, rätt svar stort, elevens svar överstruket vid fel."""
    given_line = f'<div class="given">{given_label} <s>{escape(given)}</s></div>' if given and result != "correct" else ""
    after_line = f'<div class="after">{escape(after)}</div>' if after else ""
    html(f'''<div class="word-card {'correct' if result == 'correct' else ''}" role="status">
    <div class="eyebrow">{escape(prompt)}</div>{given_line}
    <div class="prompt">{escape(answer)}</div>{after_line}</div>''')


def memory_title():
    html(f'<p class="memory-title"><span class="ic">{symbol("bulb")}</span>Så kan du minnas det</p>')


def completion(correct, answered, practiced, needs_work):
    follow_up = (f"{needs_work} av orden ligger i Ska övas och kommer tillbaka snart."
                 if needs_work else "Nästa repetition hjälper dig att minnas ännu längre.")
    html(f'''<div class="completion">{symbol('check')}<h2>Snyggt jobbat!</h2>
    <div class="score">{correct} rätt av {answered}</div>
    <p>Du har tränat <strong>{practiced} olika glosor</strong>. {follow_up}</p></div>''')
