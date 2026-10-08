"""Gemensamma SVG-motiv, valda från titel och innehåll. Inga externa bildanrop."""
import re
from html import escape

THEMES = {
    "questions": "Frågeord", "contact": "Att ha och kontaktuppgifter",
    "numbers": "Siffror", "weather": "Väder", "introduction": "Presentation",
    "calendar": "Dagar och datum", "school": "Skolsaker", "leisure": "Fritid",
    "food": "Mat och dryck", "travel": "Resor", "hotel": "På hotellet",
    "general": "Glosor",
}
BUILTIN = dict(zip([
    "1e308f6b3d8153af873ebcc1921840ee", "9744fe44c96b5e91a22eab9aacde517b",
    "d1e60aba527c58838094564ea5b026e3", "a6b0797b1a1857e5930b4b1e0562b6ff",
    "52785c71b8695a748dac66e1d22d6087", "4e3674bbd68d56488344052b0a334102",
    "d36849a293265e509d2305b843345df0", "95a6bd2a2eb158a285cbd19c17d3af84",
], list(THEMES)[:8]))
KEYWORDS = {
    "questions": "frågeord varför hur varifrån vart qué cómo dónde cuándo quién",
    "contact": "telefonnummer ålder tengo tienes tener teléfono años",
    "numbers": "siffror tal noll ett två tre cero uno dos tres cuatro cinco",
    "weather": "väder blåser kallt varmt soligt molnigt viento frío calor sol nublado",
    "introduction": "presentation heter från soy llamo llamas presentar",
    "calendar": "kalender datum måndag tisdag onsdag torsdag fredag lördag söndag lunes martes miércoles jueves viernes sábado domingo fecha",
    "school": "skola skolsaker bok blyertspenna skrivhäfte ryggsäck libro lápiz bolígrafo cuaderno mochila",
    "leisure": "fritid instrument tv-spel rida vänner amigos instrumento videojuegos caballo",
    "food": "mat dryck frukt äpple vatten bröd comida bebida fruta manzana agua pan",
    "travel": "resa resor flygplan resväska tåg viajar viaje avión maleta tren",
    "hotel": "hotell reception rumsnyckel hotel recepción habitación llave",
}


def theme_for(vocab):
    choice = vocab.get("theme", "auto")
    if isinstance(choice, str) and choice in THEMES:
        return choice
    # Även en ändrad befintlig lista ska följa sitt nya innehåll.
    title = set(re.findall(r"[^\W_]+", vocab["name"].casefold()))
    words = set(re.findall(r"[^\W_]+", " ".join(w["svenska"] + " " + " ".join(w["accepted_answers"]) for w in vocab["words"]).casefold()))
    scores = {name: len(title & set(tokens.split())) * 5 + len(words & set(tokens.split()))
              for name, tokens in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] >= 2 else "general"


def theme_svg(theme):
    motifs = {
        "questions": '<path d="M27 22h60a13 13 0 0 1 13 13v28a13 13 0 0 1-13 13H56L36 90V76h-9a13 13 0 0 1-13-13V35a13 13 0 0 1 13-13Z"/><path d="M47 40c0-17 27-17 27 0 0 9-13 9-13 20"/><circle cx="61" cy="67" r="2" fill="currentColor"/><text x="99" y="87" font-size="32" fill="currentColor" stroke="none">?</text>',
        "contact": '<rect x="46" y="14" width="48" height="83" rx="10"/><path d="M60 23h20M64 88h12"/><path d="M60 40c-4 9 8 25 18 24l5-7-10-6-4 4-5-9 3-4-6-5Z"/>',
        "numbers": '<rect x="21" y="19" width="43" height="42" rx="10"/><rect x="75" y="43" width="43" height="42" rx="10"/><text x="31" y="51" font-size="30" fill="currentColor" stroke="none">1</text><text x="85" y="75" font-size="30" fill="currentColor" stroke="none">2</text><path d="M35 78h23M46 67v23"/>',
        "weather": '<circle cx="52" cy="39" r="18"/><path d="M52 10v-5M52 68v5M23 39h-6M81 39h6M31 18l-5-5M73 18l5-5"/><path d="M57 82h49c21 0 19-32-1-32-6-21-38-18-42 2-22-3-28 30-6 30Z"/><path d="m72 89-4 9m20-9-4 9"/>',
        "introduction": '<circle cx="43" cy="36" r="13"/><path d="M21 85V74c0-29 44-29 44 0v11"/><path d="M79 23h32a9 9 0 0 1 9 9v21a9 9 0 0 1-9 9H90L78 74V62a9 9 0 0 1-9-9V32a9 9 0 0 1 10-9Z"/><text x="79" y="49" font-size="18" fill="currentColor" stroke="none">hola</text>',
        "calendar": '<rect x="27" y="24" width="86" height="70" rx="10"/><path d="M27 44h86M46 15v18M94 15v18"/><rect x="41" y="57" width="13" height="12" rx="2"/><path d="M65 62h8M88 62h8M42 81h9M65 81h8M88 81h8"/>',
        "school": '<path d="M24 30c17-8 30-5 46 3v57c-16-8-29-11-46-3V30Zm92 0c-17-8-30-5-46 3v57c16-8 29-11 46-3V30Z"/><path d="m49 16 4-7 9 5-4 7M41 32l-8 17-1 11 9-6 8-17"/>',
        "leisure": '<path d="M42 44h55c13 0 20 12 24 31 3 15-11 21-22 9l-9-10H50L38 86c-10 10-24 5-20-10l6-18c3-9 7-14 18-14Z"/><path d="M42 52v18M33 61h18"/><circle cx="94" cy="57" r="3"/><circle cx="106" cy="68" r="3"/><path d="M66 32V12l20-5v20"/><ellipse cx="60" cy="32" rx="6" ry="4"/><ellipse cx="80" cy="27" rx="6" ry="4"/>',
        "food": '<path d="M51 38c-16-12-40 5-31 31 7 23 25 26 31 20 7 6 24 3 32-20 8-26-15-43-32-31Z"/><path d="M51 38V21c11 1 17-5 18-12-13-1-20 4-18 12"/><path d="M94 40h30l-5 53H99l-5-53ZM110 40l7-23h12"/>',
        "travel": '<rect x="30" y="40" width="69" height="51" rx="9"/><path d="M51 40V29h26v11M43 40v51M86 40v51M44 91v6M85 91v6"/><path d="m99 15 28 14-28 6-8-5-9 2-3-5 13-3 3-14Z"/>',
        "hotel": '<path d="M26 92V28h61v64M17 92h107M42 92V69h29v23M42 44h10M63 44h10M42 57h10M63 57h10"/><circle cx="105" cy="45" r="10"/><path d="M105 55v26m0-5h12m-12-8h8"/>',
        "general": '<rect x="33" y="18" width="76" height="76" rx="14"/><path d="M48 69l14-34 14 34M54 55h17M88 39v30"/>',
    }
    return f'<svg viewBox="0 0 140 110" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" role="img" aria-label="{escape(THEMES[theme])}"><circle cx="70" cy="55" r="46" fill="white" fill-opacity=".6" stroke="none"/>{motifs[theme]}</svg>'
