import unicodedata
from core.answers import grade
from core.leitner import counts, due_words, initial, key, update
from core.migration import migrate_legacy
from core.trainer import Session, options_for
from data.vocabulary import builtin_lists, validate_lists


def test_answer_alternatives_unicode_punctuation_and_accents():
    assert grade(' ORDENADOR! ', ['computadora','ordenador'])[0] == 'correct'
    assert grade(unicodedata.normalize('NFD', '¿Cómo?'), ['¿Cómo?'])[0] == 'correct'
    assert grade('miercoles', ['miércoles'])[0] == 'near'
    assert grade('ano', ['año'])[0] == 'wrong'
    assert grade('ar', ['år'])[0] == 'wrong'
    assert grade('', ['perro'])[0] == 'wrong'
    assert grade('lunes', ['miércoles'])[0] == 'wrong'


def test_green_requires_delayed_unassisted_production():
    first = update(initial(), 'correct','quiz',False,100)
    assert first['box'] == 2
    assert update(first,'correct','write',False,101)['box'] == 2
    due = first['next_review']
    assert update(first,'correct','quiz',False,due)['box'] == 2
    assert update(first,'correct','cards',False,due)['box'] == 2
    assert update(first,'correct','write',True,due)['box'] == 2
    assert update(first,'correct','write',False,due)['box'] == 3
    assert update(first,'near','write',False,due)['box'] == 2
    wrong = update(first,'wrong','write',False,due)
    assert wrong['box'] == 1
    assert first['attempts'] == 1  # update has not mutated its input


def test_due_order_prioritizes_red_and_direction_is_separate():
    vocab = builtin_lists()[0]
    vocab['words'] = vocab['words'][:3]
    a,b,c = vocab['words'][:3]
    progress = {key(vocab['id'], a['id'], 'forward'):{**initial(),'box':3,'next_review':5},
                key(vocab['id'], b['id'], 'forward'):{**initial(),'box':2,'next_review':200},
                key(vocab['id'], c['id'], 'forward'):{**initial(),'box':1,'next_review':5}}
    due = due_words(vocab,progress,'forward',10,300)
    assert b not in due and due[0] == c and due[-1] == a
    assert counts(vocab,progress,'reverse')[1] == len(vocab['words'])
    renamed = {**vocab,'name':'Ett nytt namn'}
    assert counts(renamed,progress,'forward') == counts(vocab,progress,'forward')


def test_failed_word_returns_after_three_other_words_without_unbounded_loops():
    session = Session(['a','b','c','d','e'])
    session.retry_later('a',['a','b','c','d','e'])
    assert session.queue == ['a','b','c','d','a','e']
    session.retry_later('a',['a','b','c','d','e'])
    assert session.queue.count('a') == 2
    assert 'a' in session.exposed
    single = Session(['a'])
    single.retry_later('a',['a'])
    assert single.queue == ['a','a']


def test_library_and_migration():
    lists = validate_lists(builtin_lists())
    assert len(lists) == 8 and sum(len(v['words']) for v in lists) == 125
    word = lists[0]['words'][0]
    migrated,missing = migrate_legacy({word['legacy_key']:3,'_stats_flashcard_total':99,'unknown':2},lists)
    assert len(migrated) == 1 and next(iter(migrated.values()))['box'] == 3
    assert missing == ['unknown']
    computador = next(w for v in lists for w in v['words'] if w['svenska'] == 'dator')
    assert grade('computadora', computador['accepted_answers'])[0] == 'correct'
    assert grade('ordenador', computador['accepted_answers'])[0] == 'correct'


def test_quiz_does_not_offer_another_accepted_answer_as_distractor():
    words = [{'id':'a','accepted_answers':['computer','PC']},
             {'id':'b','accepted_answers':['PC']}, {'id':'c','accepted_answers':['school']}]
    assert set(options_for(words[0],words,'forward')) == {'computer','school'}
