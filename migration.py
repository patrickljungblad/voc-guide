"""Import av gammal Leitner-dictionary; statistik blir aldrig glosor."""
from core.leitner import initial, key


def migrate_legacy(legacy, lists):
    result, matched = {}, set()
    for vocab in lists:
        for word in vocab["words"]:
            legacy_key = word.get("legacy_key")
            box = legacy.get(legacy_key)
            if isinstance(box, int) and not isinstance(box, bool) and box in (1, 2, 3):
                state = initial()
                state["box"] = box
                result[key(vocab["id"], word["id"], "forward")] = state
                matched.add(legacy_key)
    missing = [x for x in legacy if not x.startswith("_stats_") and x not in matched]
    return result, missing
