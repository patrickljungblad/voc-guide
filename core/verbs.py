"""Böjning av spanska verb i presens och perfekt, för Verbtränaren.

Regelbundna verb böjs med regler. De oregelbundna formerna står utskrivna.
Perfekt (pretérito perfecto) är haber i presens + particip: he hablado = jag har pratat.
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
TENSES = {"presens": "presens", "perfekt": "perfekt"}

ENDINGS = {
    "ar": ("o", "as", "a", "amos", "áis", "an"),
    "er": ("o", "es", "e", "emos", "éis", "en"),
    "ir": ("o", "es", "e", "imos", "ís", "en"),
}

IRREGULAR_PRESENT = {
    "tener": ("tengo", "tienes", "tiene", "tenemos", "tenéis", "tienen"),
    "ser": ("soy", "eres", "es", "somos", "sois", "son"),
    "estar": ("estoy", "estás", "está", "estamos", "estáis", "están"),
    "ir": ("voy", "vas", "va", "vamos", "vais", "van"),
    "hacer": ("hago", "haces", "hace", "hacemos", "hacéis", "hacen"),
    "salir": ("salgo", "sales", "sale", "salimos", "salís", "salen"),
    "ver": ("veo", "ves", "ve", "vemos", "veis", "ven"),
    "querer": ("quiero", "quieres", "quiere", "queremos", "queréis", "quieren"),
    "poder": ("puedo", "puedes", "puede", "podemos", "podéis", "pueden"),
}

HABER = ("he", "has", "ha", "hemos", "habéis", "han")
IRREGULAR_PARTICIPLE = {
    "hacer": "hecho", "ver": "visto", "escribir": "escrito", "decir": "dicho",
    "poner": "puesto", "volver": "vuelto", "abrir": "abierto", "romper": "roto",
}

MEANINGS = {
    "hablar": "prata", "trabajar": "arbeta", "estudiar": "studera", "bailar": "dansa", "cocinar": "laga mat",
    "mirar": "titta", "necesitar": "behöva", "llamar": "ringa / kalla", "escuchar": "lyssna",
    "caminar": "gå / promenera", "comprar": "köpa", "viajar": "resa",
    "comer": "äta", "beber": "dricka", "leer": "läsa", "aprender": "lära sig", "correr": "springa",
    "vender": "sälja", "comprender": "förstå",
    "vivir": "bo / leva", "escribir": "skriva", "abrir": "öppna", "recibir": "få / ta emot",
    "subir": "gå upp / stiga", "compartir": "dela", "decidir": "bestämma",
    "tener": "ha", "ser": "vara", "estar": "vara / befinna sig", "ir": "gå / åka", "hacer": "göra",
    "salir": "gå ut", "ver": "se", "querer": "vilja", "poder": "kunna",
    "decir": "säga", "poner": "sätta / ställa", "volver": "komma tillbaka", "romper": "ha sönder",
}

# Grupperna eleven väljer bland: (rubrik, tempus, verb).
GROUPS = {
    "pres_ar": ("Regelbundna -ar", "presens", ["hablar", "trabajar", "estudiar", "bailar", "cocinar", "mirar",
                                              "necesitar", "llamar", "escuchar", "caminar", "comprar", "viajar"]),
    "pres_er": ("Regelbundna -er", "presens", ["comer", "beber", "leer", "aprender", "correr", "vender", "comprender"]),
    "pres_ir": ("Regelbundna -ir", "presens", ["vivir", "escribir", "abrir", "recibir", "subir", "compartir", "decidir"]),
    "pres_tener": ("tener", "presens", ["tener"]),
    "pres_irregular": ("Vanliga oregelbundna", "presens", ["ser", "estar", "ir", "hacer", "salir", "ver", "querer", "poder"]),
    "perf_regular": ("Regelbundna", "perfekt", ["hablar", "trabajar", "estudiar", "comer", "beber", "aprender",
                                               "vivir", "salir", "ir", "tener", "ser", "estar"]),
    "perf_irregular": ("Oregelbundna", "perfekt", ["hacer", "ver", "escribir", "decir", "poner", "volver", "abrir", "romper"]),
}
DEFAULT_GROUPS = ("pres_ar", "pres_er", "pres_ir", "pres_tener", "pres_irregular")


def meaning(verb):
    return MEANINGS.get(verb, "")


def participle(verb):
    if verb in IRREGULAR_PARTICIPLE:
        return IRREGULAR_PARTICIPLE[verb]
    return verb[:-2] + ("ado" if verb.endswith("ar") else "ido")


def conjugate(verb, person, tense="presens"):
    """Formen för ett verb, en person (0 = yo … 5 = ellos) och ett tempus."""
    if tense == "perfekt":
        return f"{HABER[person]} {participle(verb)}"
    if verb in IRREGULAR_PRESENT:
        return IRREGULAR_PRESENT[verb][person]
    return verb[:-2] + ENDINGS[verb[-2:]][person]


def table(verb, tense="presens"):
    return [conjugate(verb, person, tense) for person in range(6)]


def make_questions(groups, count, with_vosotros=True, rng=random):
    """En blandad omgång: varje fråga är ett verb, en person och ett tempus, utan onödiga upprepningar."""
    persons = [p for p in range(6) if with_vosotros or p != VOSOTROS]
    pool = list({(verb, person, GROUPS[group][1]) for group in groups for verb in GROUPS[group][2] for person in persons})
    pool.sort()
    rng.shuffle(pool)
    picked = pool[:count]
    while len(picked) < count and pool:
        picked.append(rng.choice(pool))
    return [{"verb": verb, "person": person, "tense": tense, "pronoun": rng.choice(PERSONS[person])}
            for verb, person, tense in picked]


def rule_hint(verb, tense="presens"):
    """En kort förklaring som visas när eleven svarar fel."""
    if tense == "perfekt":
        rule = "Perfekt = **haber** (he, has, ha, hemos, habéis, han) + particip."
        if verb in IRREGULAR_PARTICIPLE:
            return f"{rule} **{verb}** har ett oregelbundet particip: **{participle(verb)}**."
        return f"{rule} Regelbundet particip: -ar → **-ado**, -er/-ir → **-ido**: *{participle(verb)}*."
    if verb == "tener":
        return "**tener** är oregelbundet: *tengo* i jag-form och *ie* i stammen i tú, él och ellos."
    if verb in ("querer", "poder"):
        change = "e till ie" if verb == "querer" else "o till ue"
        return (f"**{verb}** byter {change} i stammen i alla former utom *nosotros* och *vosotros*. "
                "Tänk på en stövel: formerna i stöveln ändras.")
    if verb in IRREGULAR_PRESENT:
        return f"**{verb}** är oregelbundet – det lönar sig att plugga hela tabellen."
    ending = verb[-2:]
    return f"Regelbundet -{ending}-verb: ta bort **-{ending}** och lägg till " + ", ".join(
        f"-{e}" for e in ENDINGS[ending]) + "."
