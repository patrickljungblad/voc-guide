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


def memory_tip(word):
    return word.get("memory_tip") or TIPS.get(word["svenska"].casefold(),
        "💬 Säg ordet högt och använd det i en egen kort mening. Titta bort och försök säga det igen utan att läsa.")
