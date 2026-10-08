import json
import base64
from email.message import Message
from io import BytesIO
from unittest.mock import Mock
from urllib.error import HTTPError
import pytest
from services.database import ServiceError
from services import speech
from ui.audio import speech_html


def test_generation_escapes_text_reuses_clip_and_never_exposes_key(tmp_path, monkeypatch):
    monkeypatch.setenv('AUDIO_BANK_PATH', str(tmp_path / 'audio_bank.json'))
    payload = b'ID3-test-audio'
    response = BytesIO(payload)
    response.headers = Message()
    response.headers['Content-Type'] = 'audio/mpeg'
    opener = Mock()
    opener.open.return_value = response
    monkeypatch.setattr(speech, 'build_opener', lambda *args: opener)
    attack = '</voice><audio src="https://bad.invalid"/>'
    first = speech.get_or_create(attack, 'es-MX', 'es-MX-DaliaNeural', 'secret-api-key', 'swedencentral')
    second = speech.get_or_create(attack, 'es-MX', 'es-MX-DaliaNeural', 'secret-api-key', 'swedencentral')
    assert first == second == payload and opener.open.call_count == 1
    request = opener.open.call_args.args[0]
    assert b'<audio' not in request.data and b'&lt;/voice&gt;' in request.data
    html = speech_html([{'target':[attack]}], 'Spanska')
    assert 'data:audio/mpeg;base64,' in html and 'secret-api-key' not in html
    assert attack not in html
    bank = json.loads((tmp_path / 'audio_bank.json').read_text())
    assert 'secret-api-key' not in json.dumps(bank)
    assert len(bank['clips']) == 1


def test_provider_failure_keeps_created_clips_and_redacts_response(tmp_path, monkeypatch):
    monkeypatch.setenv('AUDIO_BANK_PATH', str(tmp_path / 'audio_bank.json'))
    key = speech.clip_key('hola', 'es-MX')
    speech.store_clips({key: {'text':'hola', 'language':'es-MX', 'voice':'es-MX-DaliaNeural', 'mp3':base64.b64encode(b'ID3-existing').decode()}})
    opener = Mock()
    opener.open.side_effect = HTTPError('https://endpoint', 429, 'private-key', {}, None)
    monkeypatch.setattr(speech, 'build_opener', lambda *args: opener)
    with pytest.raises(ServiceError, match='gräns') as error:
        speech.synthesize('hola', 'es-MX-DaliaNeural', 'private-key', 'swedencentral')
    assert 'private-key' not in str(error.value)
    assert (tmp_path / 'audio_bank.json').exists()
    assert speech.load_bank()['clips'][key]['text'] == 'hola'


def test_invalid_region_or_voice_never_sends_request(monkeypatch):
    opener = Mock()
    monkeypatch.setattr(speech, 'build_opener', lambda *args: opener)
    with pytest.raises(ServiceError):
        speech.synthesize('hola', 'es-MX-DaliaNeural', 'key', 'example.com/path')
    with pytest.raises(ServiceError):
        speech.get_or_create('hola', 'sv-SE', 'es-MX-DaliaNeural', 'key', 'swedencentral')
    assert not opener.open.called


def test_activated_spanish_variant_wins_even_if_previous_variant_is_cached(tmp_path, monkeypatch):
    monkeypatch.setenv('AUDIO_BANK_PATH', str(tmp_path / 'audio_bank.json'))
    clips = {speech.clip_key('hola', tag): {'text':'hola', 'language':tag, 'voice':voice, 'mp3':base64.b64encode(b'ID3-audio').decode()}
             for tag, voice in [('es-MX','es-MX-DaliaNeural'),('es-CL','es-CL-CatalinaNeural')]}
    speech.store_clips(clips, {'es':'es-CL'})
    assert speech.audio_for('hola', 'es-MX', speech.load_bank())['voice'] == 'es-CL-CatalinaNeural'
    speech.store_clips({}, {'es':'es-MX'})
    assert speech.audio_for('hola', 'es-MX', speech.load_bank())['voice'] == 'es-MX-DaliaNeural'


def fake_clip(text, language, voice, api_key, region):
    return speech.clip_key(text, language), {'text': text, 'language': language, 'voice': voice,
                                             'mp3': base64.b64encode(b'ID3-' + text.encode()).decode()}


def test_generate_paces_requests_retries_rate_limit_and_saves_in_batches(monkeypatch):
    calls, saved, sleeps = [], [], []
    def make(text, language, voice, api_key, region):
        calls.append(text)
        if text == 'b' and calls.count('b') == 1:
            raise speech.RateLimited('gräns')
        return fake_clip(text, language, voice, api_key, region)
    monkeypatch.setattr(speech, 'make_clip', make)
    missing = [(t, 'es-MX', 'es-MX-DaliaNeural') for t in 'abcdefghijklmnopq']
    done = speech.generate(missing, 'k', 'swedencentral', lambda batch: saved.append(dict(batch)), sleep=sleeps.append)
    assert done == 17 and calls.count('b') == 2
    assert [len(b) for b in saved] == [15, 2]
    assert 20 in sleeps and sleeps.count(3.1) == 16


def test_generate_keeps_finished_clips_when_azure_fails(monkeypatch):
    saved = []
    def make(text, language, voice, api_key, region):
        if text == 'c':
            raise ServiceError('Kontrollera ljudtjänstens nyckel och region.')
        return fake_clip(text, language, voice, api_key, region)
    monkeypatch.setattr(speech, 'make_clip', make)
    missing = [(t, 'sv-SE', 'sv-SE-SofieNeural') for t in 'abcd']
    with pytest.raises(ServiceError):
        speech.generate(missing, 'k', 'swedencentral', saved.append, sleep=lambda s: None)
    assert [sorted(c['text'] for c in b.values()) for b in saved] == [['a', 'b']]


def test_local_database_stores_audio_for_teachers_only(tmp_path):
    from services.database import LocalDatabase
    db = LocalDatabase(tmp_path / 'db.sqlite3', 'a-long-test-password')
    teacher = db.teacher_login('a-long-test-password')['token']
    clip_id, clip = fake_clip('hola', 'es-MX', 'es-MX-DaliaNeural', '', '')
    assert db.get_audio() == {}
    assert db.save_audio(teacher, {clip_id: clip}) == 1
    assert db.get_audio() == {clip_id: clip}
    with pytest.raises(ServiceError):
        db.save_audio(teacher, {'wrong-key': clip})
    db.create_user(teacher, 'Test', '2A', '0123')
    student = db.authenticate('Test', '2A', '0123')['token']
    with pytest.raises(ServiceError):
        db.save_audio(student, {clip_id: clip})


def test_saved_database_clips_are_used_in_playback():
    clip_id, clip = fake_clip('hola', 'es-MX', 'es-MX-DaliaNeural', '', '')
    html = speech_html([{'target': ['hola']}], 'Spanska', extra_clips={clip_id: clip})
    assert 'data:audio/mpeg;base64,' + clip['mp3'] in html
    assert 'data:audio/mpeg' not in speech_html([{'target': ['hola']}], 'Spanska')
