from copy import deepcopy
from io import BytesIO
from pypdf import PdfReader
import pytest
from data.vocabulary import builtin_lists
from services.print_quiz import quiz_versions, quiz_pdf


def test_ab_use_same_words_in_different_orders_and_do_not_mutate_list():
    vocab = builtin_lists()[0]
    before = deepcopy(vocab)
    ids = [w['id'] for w in vocab['words']][1:6]
    versions = quiz_versions(vocab, ids, shuffled=False, two_versions=True, seed=14)
    a, b = [[w['id'] for w in versions[v]] for v in ('A', 'B')]
    assert a == ids and set(a) == set(b) and a != b
    assert vocab == before
    with pytest.raises(ValueError):
        quiz_versions(vocab, ids[:1], two_versions=True)
    with pytest.raises(ValueError):
        quiz_versions(vocab, ['missing'])


@pytest.mark.parametrize('direction', ['forward', 'reverse'])
def test_pdf_has_separate_facit_and_correct_numbered_answers(direction):
    vocab = builtin_lists()[0]
    versions = quiz_versions(vocab, [w['id'] for w in vocab['words']][:5], two_versions=True, seed=123)
    quiz = PdfReader(BytesIO(quiz_pdf(vocab, versions, direction)))
    answer = PdfReader(BytesIO(quiz_pdf(vocab, versions, direction, answers=True)))
    assert len(quiz.pages) == len(answer.pages) == 2
    for i, version in enumerate(('A', 'B')):
        qtext, atext = quiz.pages[i].extract_text(), answer.pages[i].extract_text()
        assert 'Version ' + version in qtext and 'Version ' + version in atext
        assert 'Namn:' in qtext and 'Klass:' in qtext and 'Datum:' in qtext
        cursor = 0
        for word in versions[version]:
            solutions = word['accepted_answers'] if direction == 'forward' else word['swedish_answers']
            expected = '; '.join(solutions)
            assert expected not in qtext
            cursor = atext.index(expected, cursor) + len(expected)


def test_long_titles_and_many_answers_paginate_without_losing_text():
    vocab = deepcopy(builtin_lists()[0])
    vocab['name'] = 'Lång gloslista med åäö och ¿Qué? ' * 5
    vocab['words'][0]['accepted_answers'] = [('alternativ%d ' % i) * 18 for i in range(20)]
    versions = quiz_versions(vocab, [vocab['words'][0]['id']], shuffled=False)
    pdf = PdfReader(BytesIO(quiz_pdf(vocab, versions, answers=True)))
    text = '\n'.join(page.extract_text() for page in pdf.pages)
    assert 'alternativ0' in text and 'alternativ19' in text
