"""Sessionsdata är fristående från sparat lärande."""
from dataclasses import dataclass, field
import random
from uuid import uuid4
from core.answers import normalize


@dataclass
class Session:
    queue: list[str]
    mode: str = "auto"
    index: int = 0
    correct: int = 0
    answered: int = 0
    streak: int = 0
    start_green: int = 0
    hints: int = 0
    tip: bool = False
    flipped: bool = False
    feedback: dict | None = None
    options: list[str] = field(default_factory=list)
    exposed: set[str] = field(default_factory=set)
    retries: set[str] = field(default_factory=set)
    turn_id: str = field(default_factory=lambda: uuid4().hex)

    @property
    def done(self):
        return self.index >= len(self.queue)

    @property
    def current(self):
        return None if self.done else self.queue[self.index]

    def advance(self):
        self.index += 1
        self.hints = 0
        self.tip = self.flipped = False
        self.feedback = None
        self.options = []
        self.turn_id = uuid4().hex

    def retry_later(self, word_id, all_ids):
        if word_id in self.retries or len(self.queue) >= 20:
            return
        self.retries.add(word_id)
        self.exposed.add(word_id)
        tail = self.queue[self.index + 1:]
        other = [x for x in all_ids if x != word_id and x not in tail[:3]]
        # Tillför högst tre andra ord så att svaret hinner försvinna ur arbetsminnet.
        fillers = other[:max(0, 3 - len(tail))]
        insertion = self.index + 1 + min(3, len(tail) + len(fillers))
        self.queue[self.index + 1:self.index + 1] = fillers
        self.queue.insert(insertion, word_id)


def options_for(word, words, direction):
    field = "accepted_answers" if direction == "forward" else "swedish_answers"
    correct = word[field][0]
    accepted = {normalize(x) for x in word[field]}
    others = {}
    for other in words:
        if other["id"] != word["id"] and not accepted.intersection(normalize(x) for x in other[field]):
            option = other[field][0]
            others.setdefault(normalize(option), option)
    options = random.sample(list(others.values()), min(3, len(others))) + [correct]
    random.shuffle(options)
    return options
