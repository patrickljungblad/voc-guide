"""Minnesstrategier: ordspecifika tips, roterande strategier och elevens egna knep."""
from zlib import crc32
from core.answers import normalize
from pedagogy.word_tips import WORD_TIPS

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
    """Lärarens tips i listan går först, sedan ordets eget tips, sist en roterande strategi."""
    if word.get("memory_tip"):
        return word["memory_tip"]
    for answer in word["accepted_answers"]:
        tip = WORD_TIPS.get(normalize(answer))
        if tip:
            return tip
    return _strategy(word)


OWN_TIP_MAX = 200


def own_tip(progress, keys):
    """Elevens eget knep sparas på ordets lådtillstånd; samma knep gäller båda riktningarna."""
    for progress_key in keys:
        tip = progress.get(progress_key, {}).get("own_tip")
        if tip:
            return tip
    return ""
