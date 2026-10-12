import json
import re
from pathlib import Path
from uuid import uuid4


def builtin_lists():
    return json.loads(Path(__file__).with_name("vocabulary.json").read_text(encoding="utf-8"))


def validate_lists(lists):
    if not isinstance(lists, list) or not 1 <= len(lists) <= 100:
        raise ValueError("Ange 1–100 gloslistor.")
    ids = set()
    for vocab in lists:
        for field in ("id", "name", "category", "language"):
            if not isinstance(vocab.get(field), str) or not 1 <= len(vocab[field]) <= 160:
                raise ValueError(f"Listan saknar giltigt {field}.")
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", vocab["id"]):
            raise ValueError("List-ID får bara innehålla bokstäver, siffror, _ och -.")
        if vocab["id"] in ids:
            raise ValueError("List-ID måste vara unika.")
        ids.add(vocab["id"])
        if not isinstance(vocab.get("words"), list) or not 1 <= len(vocab["words"]) <= 300:
            raise ValueError("Varje lista behöver 1–300 ord.")
        word_ids = set()
        for word in vocab["words"]:
            if not isinstance(word.get("id"), str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,160}", word["id"]) or word["id"] in word_ids:
                raise ValueError("Ord-ID saknas eller är dubblerade.")
            word_ids.add(word["id"])
            if not isinstance(word.get("svenska"), str) or not 1 <= len(word["svenska"]) <= 300:
                raise ValueError("Svensk betydelse saknas.")
            for field in ("accepted_answers", "swedish_answers"):
                values = word.get(field)
                if not isinstance(values, list) or not 1 <= len(values) <= 20 or any(not isinstance(x, str) or not x.strip() or len(x) > 300 for x in values):
                    raise ValueError("Varje ord behöver giltiga svarsalternativ i båda riktningarna.")
            if not isinstance(word.get("memory_tip", ""), str) or len(word.get("memory_tip", "")) > 2000:
                raise ValueError("Minnestipset är för långt.")
    return lists


SEPARATORS = ("\t", " = ", "=", " – ", " — ", " - ", ";")


def split_line(line):
    """Delar en rad i svenska, målspråk och eventuellt minnestips.

    Tabb (från kalkylblad) går först. Annars godtas =, ett tankstreck eller bindestreck med
    mellanslag runt (så att t.ex. "tv-spel" inte delas) och semikolon.
    """
    for separator in SEPARATORS:
        if separator in line:
            parts = [part.strip() for part in line.split(separator)]
            if separator != "\t" and len(parts) > 3:
                parts = parts[:2] + [separator.strip().join(parts[2:])]
            return parts
    return [line.strip()]


def parse_words(text):
    """En glosa per rad: svenska, målspråk (alternativ med |) och valfritt minnestips."""
    words = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        parts = split_line(line)
        if not 2 <= len(parts) <= 3 or not parts[0] or not parts[1]:
            raise ValueError(f"Rad {number} ({line.strip()[:40]}) behöver svenska och målspråk, till exempel: hund = perro")
        sv, target = parts[:2]
        words.append({"id": uuid4().hex, "svenska": sv.replace("|", ", "),
                      "swedish_answers": [x.strip() for x in sv.split("|") if x.strip()],
                      "accepted_answers": [x.strip() for x in target.split("|") if x.strip()],
                      "memory_tip": parts[2] if len(parts) == 3 else ""})
    if not words:
        raise ValueError("Skriv minst en glosa, till exempel: hund = perro")
    return words
