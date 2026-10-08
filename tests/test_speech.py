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
