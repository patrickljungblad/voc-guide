"""Tre lådor, tidsstyrd repetition och försiktig bedömning av hjälpta svar."""
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

INTERVALS = {1: 86400, 2: 3 * 86400, 3: 7 * 86400}
LABELS = {1: "Ska övas", 2: "På väg", 3: "Kan bra"}


def key(list_id, word_id, direction):
    return f"{list_id}:{word_id}:{direction}"


def initial():
    return {"box": 1, "attempts": 0, "correct": 0, "last_reviewed": None, "next_review": 0}


def update(previous, result, mode, assisted, now):
    state = deepcopy(previous or initial())
    old_box = state["box"]
    due = now >= state["next_review"]
    state["attempts"] += 1
    state["last_reviewed"] = now
    if result == "wrong":
        # Ett steg ner i taget: ett ord man har kunnat förlorar inte allt på ett fel.
        state["box"] = max(1, old_box - 1)
        state["next_review"] = now + 600
    elif result == "near":
        state["next_review"] = min(state["next_review"], now + 600)
    else:
        state["correct"] += 1
        if due and not assisted and mode != "cards":
            if old_box == 1:
                state["box"] = 2
            elif mode == "write":
                state["box"] = 3
        if due:
            state["next_review"] = now + (600 if assisted else INTERVALS[state["box"]])
    return state


def due_words(vocab, progress, direction, now, limit=10):
    words = [w for w in vocab["words"] if progress.get(key(vocab["id"], w["id"], direction), initial())["next_review"] <= now]
    return sorted(words, key=lambda w: (
        progress.get(key(vocab["id"], w["id"], direction), initial())["box"],
        progress.get(key(vocab["id"], w["id"], direction), initial())["next_review"],
    ))[:limit]


def counts(vocab, progress, direction):
    return {box: sum(progress.get(key(vocab["id"], w["id"], direction), initial())["box"] == box for w in vocab["words"]) for box in (1, 2, 3)}


def next_review_text(timestamp, now, zone="Europe/Stockholm"):
    """Hur länge eleven ska vänta, i ord: "om 10 minuter", "i morgon", "om 3 dagar"."""
    seconds = timestamp - now
    if seconds < 3600:
        return f"om {max(1, round(seconds / 60))} minuter"
    tz = ZoneInfo(zone)
    days = (datetime.fromtimestamp(timestamp, tz).date() - datetime.fromtimestamp(now, tz).date()).days
    if days <= 0:
        return "senare i dag"
    if days == 1:
        return "i morgon"
    return f"om {days} dagar"
