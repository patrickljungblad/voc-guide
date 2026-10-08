"""Läraren skapar ljud en gång. Elevens uppspelning gör inga API-anrop."""
import base64
import hashlib
import json
import os
import re
import threading
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler
from uuid import uuid4
from xml.sax.saxutils import escape
from services.database import ServiceError

VOICES = {
    "es-MX": {"es-MX-DaliaNeural": "Dalia – spanska (Mexiko)", "es-MX-JorgeNeural": "Jorge – spanska (Mexiko)"},
    "es-CL": {"es-CL-CatalinaNeural": "Catalina – spanska (Chile)", "es-CL-LorenzoNeural": "Lorenzo – spanska (Chile)"},
    "sv-SE": {"sv-SE-SofieNeural": "Sofie – svenska", "sv-SE-MattiasNeural": "Mattias – svenska"},
    "en-GB": {"en-GB-SoniaNeural": "Sonia – engelska (Storbritannien)", "en-GB-RyanNeural": "Ryan – engelska (Storbritannien)"},
}
ROOT = Path(__file__).resolve().parents[1]
LOCK = threading.Lock()


def clip_key(text, language):
    normalized = unicodedata.normalize("NFC", text.strip())
    return hashlib.sha256((language.lower() + "\n" + normalized).encode("utf-8")).hexdigest()


def bank_path():
    return Path(os.environ.get("AUDIO_BANK_PATH", str(ROOT / "runtime" / "audio_bank.json")))


def load_bank():
    clips = {}
    preferred = {}
    for path in (ROOT / "data" / "audio_bank.json", bank_path()):
        try:
            incoming = json.loads(path.read_text(encoding="utf-8"))
            if incoming.get("version") != 1:
                continue
            for prefix, tag in incoming.get("preferred", {}).items():
                if isinstance(tag, str) and tag in VOICES and tag[:2] == prefix:
                    preferred[prefix] = tag
            for key, clip in incoming.get("clips", {}).items():
                if not isinstance(clip, dict) or not all(isinstance(clip.get(k), str) for k in ("text", "language", "voice", "mp3")):
                    continue
                if key != clip_key(clip["text"], clip["language"]) or not 1 <= len(clip["mp3"]) <= 700_000:
                    continue
                try:
                    base64.b64decode(clip["mp3"], validate=True)
                except ValueError:
                    continue
                clips[key] = clip
        except (OSError, ValueError, AttributeError, TypeError):
            continue
    return {"version": 1, "clips": clips, "preferred": preferred}


def store_clips(clips, preferred=None):
    with LOCK:
        bank = load_bank()
        bank["clips"].update(clips)
        if preferred:
            bank["preferred"].update(preferred)
        path = bank_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + "." + uuid4().hex + ".tmp")
        try:
            temp.write_text(json.dumps(bank, ensure_ascii=False), encoding="utf-8")
            temp.replace(path)
        finally:
            temp.unlink(missing_ok=True)
    return bank


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def synthesize(text, voice, api_key, region):
    supported = {voice for voices in VOICES.values() for voice in voices}
    if not api_key or not re.fullmatch(r"[a-z0-9]{3,40}", region or ""):
        raise ServiceError("Lägg till AZURE_SPEECH_KEY och AZURE_SPEECH_REGION i Streamlit Secrets.")
    if voice not in supported or not isinstance(text, str) or not 1 <= len(text.strip()) <= 300:
        raise ServiceError("Ogiltig text eller röst.")
    language = voice[:5]
    # Inget användarinnehåll kan skapa SSML-taggar eller externa ljudreferenser.
    clean = "".join(c for c in text.strip() if ord(c) >= 32 or c in "\n\t")
    ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language}"><voice name="{voice}">{escape(clean)}</voice></speak>'
    request = Request(f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1", data=ssml.encode("utf-8"),
                      headers={"Ocp-Apim-Subscription-Key": api_key, "Content-Type": "application/ssml+xml",
                               "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3", "User-Agent": "GlosFlow"}, method="POST")
    try:
        with build_opener(NoRedirect()).open(request, timeout=20) as response:
            audio = response.read(500_001)
            if response.headers.get_content_type() not in ("audio/mpeg", "audio/mp3", "application/octet-stream") or not audio or len(audio) > 500_000:
                raise ServiceError("Ljudtjänsten gav inget giltigt ljud. Försök igen.")
            return audio
    except HTTPError as error:
        message = {401: "Kontrollera ljudtjänstens nyckel och region.", 403: "Ljudtjänsten nekade åtkomst. Kontrollera abonnemang och region.",
                   429: "Ljudtjänstens gräns har nåtts. Vänta en stund och försök igen."}.get(error.code, "Ljudtjänsten kunde inte skapa ljudet. Försök igen.")
        raise ServiceError(message) from None
    except (URLError, TimeoutError, OSError):
        raise ServiceError("Ljudtjänsten kunde inte nås. Redan skapade ljud finns kvar; försök igen senare.") from None


def get_or_create(text, language, voice, api_key, region):
    if voice not in VOICES.get(language, {}):
        raise ServiceError("Rösten matchar inte det valda språket.")
    key = clip_key(text, language)
    existing = load_bank()["clips"].get(key)
    if existing and existing["voice"] == voice:
        return base64.b64decode(existing["mp3"])
    audio = synthesize(text, voice, api_key, region)
    store_clips({key: {"text": text.strip(), "language": language, "voice": voice, "mp3": base64.b64encode(audio).decode("ascii")}})
    return audio


def audio_for(text, language, bank):
    # Samma förinspelade latinamerikanska röst för es-MX/es-CL i elevvyn.
    languages = [language] if language else []
    if language and language.lower().startswith("es"):
        languages = [bank.get("preferred", {}).get("es", "es-MX"), *languages, "es-MX", "es-CL"]
    for tag in languages:
        clip = bank["clips"].get(clip_key(text, tag))
        if clip:
            return {"src": "data:audio/mpeg;base64," + clip["mp3"], "voice": clip["voice"]}
    return None
