from copy import deepcopy
from data.vocabulary import builtin_lists
from ui.themes import BUILTIN, theme_for


def test_existing_lists_get_meaningful_themes_without_changing_ids():
    for vocab in builtin_lists():
        assert theme_for(vocab) == BUILTIN[vocab['id']]
    changed = deepcopy(builtin_lists()[0])
    changed['theme'] = 'weather'
    assert theme_for(changed) == 'weather'
    changed['theme'] = 'auto'
    changed['name'] = 'Mat och dryck'
    changed['words'] = [{'svenska':'bröd och vatten', 'accepted_answers':['pan y agua']}]
    assert theme_for(changed) == 'food'
