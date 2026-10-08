from ui.audio import language_tag, speech_html
from ui.navigation import list_url


def test_share_link_contains_only_stable_list_id():
    assert list_url('https://example.streamlit.app/?token=private#anchor','stable_id') == 'https://example.streamlit.app/?lista=stable_id'
    assert list_url('http://localhost:8501/app','id') == 'http://localhost:8501/app?lista=id'


def test_untrusted_vocabulary_cannot_close_script_tag():
    attack = '</script><script>alert(1)</script>'
    html = speech_html([{'target':[attack]}], 'Spanska')
    assert attack not in html
    assert '\\u003c/script\\u003e' in html
    assert html.count('</script>') == 1
    assert language_tag('Spanska') == 'es-MX'
    assert language_tag('English') == 'en-GB'
    assert language_tag('fr-CA') == 'fr-CA'
    assert language_tag('Ett okänt språk') is None
