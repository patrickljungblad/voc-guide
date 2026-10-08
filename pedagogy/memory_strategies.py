"""Minnesstrategier: ordspecifika tips, roterande strategier och elevens egna knep."""
from zlib import crc32

TIPS = {
    "dator": "🔗 Computadora liknar engelskans computer. Tänk på din egen dator och säg ordet högt.",
    "bok": "🔗 Libro: koppla boken till library, ett bibliotek fullt av böcker.",
    "telefonnummer": "🔗 Número de teléfono: du känner redan igen nummer och telefon.",
    "jag har": "🧩 Tengo är jag-formen av tener. Lägg märke till -o. Säg: Tengo un libro.",
    "att ha": "💬 Sätt tener i ett uttryck: tener un libro, att ha en bok.",
    "det är soligt": "🔗 Sol betyder sol. Se en sol framför dig och säg: Hace sol.",
    "det är kallt": "💬 Föreställ dig en kall morgon: Hace frío. Säg meningen högt.",
    "onsdag": "🧩 Dela upp miércoles: miér-co-les. Betoningen och accenten ligger på första delen.",
    "spanska": "🔗 Español och Spanish: koppla till ett språk du redan kan namnet på.",
    "engelska": "🔗 Inglés liknar engelska. Observera accenten över é.",
}

# Varje ord får alltid samma strategi, så att eleven känner igen den nästa gång.
STRATEGIES = (
    ("🔗", "Hitta en likhet",
     "Låter {target} som något du redan kan, på svenska, engelska eller ett annat språk? "
     "Koppla ihop dem. Ju tokigare kopplingen är, desto lättare fastnar den."),
    ("🖼️", "Se en bild",
     "Blunda och se {svenska} framför dig, så tydligt du kan. Föreställ dig att ordet {target} "
     "står skrivet på bilden med stora bokstäver."),
    ("🎭", "Gör en tokig mening",
     "Hitta på en kort och gärna rolig mening där {target} ingår. Säg den högt."),
    ("🧩", "Dela upp ordet",
     "Säg {target} långsamt, en bit i taget. Vilken del är svårast? Säg den delen extra tydligt."),
    ("🗣️", "Säg och dölj",
     "Säg {target} högt tre gånger. Titta bort och försök säga det igen utan att läsa."),
)


def _strategy(word):
    icon, title, text = STRATEGIES[crc32(word["id"].encode()) % len(STRATEGIES)]
    target = word["accepted_answers"][0]
    return f"{icon} **{title}.** " + text.format(target=f"**{target}**", svenska=f"*{word['svenska']}*")


def memory_tip(word):
    """Lärarens tips i listan går först, sedan inbyggda tips, sist en roterande strategi."""
    return word.get("memory_tip") or TIPS.get(word["svenska"].casefold()) or _strategy(word)


OWN_TIP_MAX = 200


def own_tip(progress, keys):
    """Elevens eget knep sparas på ordets lådtillstånd; samma knep gäller båda riktningarna."""
    for progress_key in keys:
        tip = progress.get(progress_key, {}).get("own_tip")
        if tip:
            return tip
    return ""
