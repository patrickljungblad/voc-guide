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


def parse_words(text):
    """Tabbseparerat: svenska, målspråk (alternativ med |), valfritt minnestips."""
    words = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if not 2 <= len(parts) <= 3:
            raise ValueError("Använd en tabb mellan svenska, målspråk och eventuellt minnestips.")
        sv, target = parts[:2]
        words.append({"id": uuid4().hex, "svenska": sv.strip(),
                      "swedish_answers": [x.strip() for x in sv.split("|")],
                      "accepted_answers": [x.strip() for x in target.split("|")],
                      "memory_tip": parts[2].strip() if len(parts) == 3 else ""})
    return words
