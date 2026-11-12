"""Böjning av spanska verb i presens, för Verbtränaren.

Verben är valda ur kursens gloslistor. Regelbundna verb böjs med regler, verb med
vokalväxling (e→ie, o→ue, u→ue) böjs med regel + undantag, och de helt oregelbundna
står utskrivna.
"""
import random

PERSONS = (
    ("yo",),
    ("tú",),
    ("él", "ella", "usted"),
    ("nosotros", "nosotras"),
    ("vosotros", "vosotras"),
    ("ellos", "ellas", "ustedes"),
)
PERSON_NAMES = ("yo", "tú", "él / ella / usted", "nosotros / nosotras", "vosotros / vosotras", "ellos / ellas / ustedes")
VOSOTROS = 4

ENDINGS = {
    "ar": ("o", "as", "a", "amos", "áis", "an"),
    "er": ("o", "es", "e", "emos", "éis", "en"),
    "ir": ("o", "es", "e", "imos", "ís", "en"),
}

IRREGULAR = {
    "ser": ("soy", "eres", "es", "somos", "sois", "son"),
    "estar": ("estoy", "estás", "está", "estamos", "estáis", "están"),
    "tener": ("tengo", "tienes", "tiene", "tenemos", "tenéis", "tienen"),
    "ir": ("voy", "vas", "va", "vamos", "vais", "van"),
    "hacer": ("hago", "haces", "hace", "hacemos", "hacéis", "hacen"),
    "salir": ("salgo", "sales", "sale", "salimos", "salís", "salen"),
    "ver": ("veo", "ves", "ve", "vemos", "veis", "ven"),
}

# Vokalväxling i alla former utom vi och ni ("stöveln").
STEM_CHANGE = {"querer": ("e", "ie"), "poder": ("o", "ue"), "dormir": ("o", "ue"), "jugar": ("u", "ue")}

# Grupper som eleven väljer bland, med svensk betydelse.
GROUPS = {
    "ar": ("Regelbundna -ar", {
        "hablar": "prata", "trabajar": "arbeta", "estudiar": "studera", "bailar": "dansa",
        "cocinar": "laga mat", "mirar": "titta", "necesitar": "behöva", "llamar": "ringa / kalla",
        "descansar": "vila", "dibujar": "rita", "entrenar": "träna", "chatear": "chatta",
    }),
    "er_ir": ("Regelbundna -er och -ir", {
        "comer": "äta", "beber": "dricka", "leer": "läsa", "aprender": "lära sig", "correr": "springa",
        "vivir": "bo / leva", "escribir": "skriva", "abrir": "öppna", "recibir": "få / ta emot",
    }),
    "stem": ("Vokalväxling (e→ie, o→ue)", {
        "querer": "vilja", "poder": "kunna", "dormir": "sova", "jugar": "spela / leka",
    }),
    "irregular": ("Oregelbundna", {
        "ser": "vara", "estar": "vara / befinna sig", "tener": "ha", "ir": "gå / åka",
        "hacer": "göra", "salir": "gå ut", "ver": "se",
    }),
}


def meaning(verb):
    for _, verbs in GROUPS.values():
        if verb in verbs:
            return verbs[verb]
    return ""


def conjugate(verb, person):
    """Presensform för ett verb och en person (0 = yo … 5 = ellos)."""
    if verb in IRREGULAR:
        return IRREGULAR[verb][person]
    stem, ending = verb[:-2], ENDINGS[verb[-2:]][person]
    if verb in STEM_CHANGE and person not in (3, 4):
        old, new = STEM_CHANGE[verb]
        cut = stem.rfind(old)
        stem = stem[:cut] + new + stem[cut + len(old):]
    return stem + ending


def table(verb):
    return [conjugate(verb, person) for person in range(6)]


def make_questions(groups, count, with_vosotros=True, rng=random):
    """En blandad omgång: varje fråga är ett verb och en person, utan upprepningar i onödan."""
    verbs = [verb for group in groups for verb in GROUPS[group][1]]
    persons = [p for p in range(6) if with_vosotros or p != VOSOTROS]
    pool = [(verb, person) for verb in verbs for person in persons]
    rng.shuffle(pool)
    picked = pool[:count]
    while len(picked) < count and pool:
        picked.append(rng.choice(pool))
    return [{"verb": verb, "person": person, "pronoun": rng.choice(PERSONS[person])} for verb, person in picked]


def rule_hint(verb):
    """En kort förklaring som visas när eleven svarar fel."""
    if verb in IRREGULAR:
        return f"**{verb}** är oregelbundet – det lönar sig att plugga hela tabellen."
    if verb in STEM_CHANGE:
        old, new = STEM_CHANGE[verb]
        return (f"**{verb}** byter {old} till {new} i stammen i alla former utom *nosotros* och *vosotros*. "
                "Tänk på en stövel: formerna i stöveln ändras.")
    ending = verb[-2:]
    return f"Regelbundet -{ending}-verb: ta bort **-{ending}** och lägg till " + ", ".join(
        f"-{e}" for e in ENDINGS[ending]) + "."
