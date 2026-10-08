"""Lärarens panel för AI-röster: välj röster, provlyssna och skapa ljud som sparas i databasen."""
import base64
import math
import streamlit as st
from services.config import setting
from services.database import ServiceError
from services.speech import VOICES, clip_key, generate, load_bank, make_clip
from ui.audio import language_tag, saved_clips

LANGUAGE_NAMES = {"es": "spanska", "en": "engelska", "sv": "svenska"}


def voice_language(vocab, spanish):
    """Språkkoden ljudet skapas för. Spanska följer lärarens val av variant."""
    tag = language_tag(vocab["language"])
    if tag and tag.lower().startswith("es"):
        return spanish
    return tag if tag in VOICES else None


def needed(vocabs, voices, spanish):
    """Alla uttryck som ska läsas upp: målspråket och de svenska orden, utan dubbletter."""
    requests = {}
    for vocab in vocabs:
        target = voice_language(vocab, spanish)
        for word in vocab["words"]:
            if target:
                for text in word["accepted_answers"]:
                    requests.setdefault((text.strip(), target), voices[target])
            for text in [word["svenska"], *word["swedish_answers"]]:
                requests.setdefault((text.strip(), "sv-SE"), voices["sv-SE"])
    return [(text, language, voice) for (text, language), voice in requests.items() if text]


def setup_help():
    st.info("För att skapa AI-röster behöver appen en nyckel till Microsofts tjänst Azure Speech. "
            "Under tiden används den bästa rösten som finns på elevens enhet.")
    with st.expander("Så kopplar du Azure Speech (ca 10 minuter)", expanded=True):
        st.markdown(
            "1. Skapa ett gratis Microsoft Azure-konto på **portal.azure.com**.\n"
            "2. Sök efter **Speech** i portalen och skapa en ny Speech-resurs. Välj prisnivån **Free F0** "
            "och en region nära dig, till exempel **Sweden Central**.\n"
            "3. Öppna resursen när den är klar och gå till **Keys and Endpoint**. Kopiera **KEY 1** och "
            "**Location/Region** (t.ex. `swedencentral`).\n"
            "4. Öppna din app på **share.streamlit.io** → menyn med tre punkter → **Settings** → **Secrets** och lägg till:\n\n"
            "```toml\nAZURE_SPEECH_KEY = \"din-nyckel\"\nAZURE_SPEECH_REGION = \"swedencentral\"\n```\n"
            "5. Spara. Appen startar om, och sedan kan du skapa ljud här.")
        st.caption("Gratisnivån räcker gott för glosor, men den skapar högst 20 ljud per minut. "
                   "Nyckeln stannar i Streamlit och skickas aldrig till eleverna.")


def speech_panel(db, token, lists):
    st.subheader("Naturliga AI-röster")
    st.caption("Skapa riktiga röster till glosorna en gång. Ljuden sparas i databasen och spelas upp för alla elever, "
               "på alla enheter. Inga nya ljud skapas när eleverna lyssnar.")
    key, region = setting("AZURE_SPEECH_KEY"), setting("AZURE_SPEECH_REGION")
    configured = bool(key and region)
    if not configured:
        setup_help()

    try:
        stored = db.get_audio() or {}
        storage_ok = True
    except ServiceError:
        stored, storage_ok = {}, False
        st.warning("Databasen kan inte spara ljud ännu. Uppdatera koden i Google Apps Script enligt avsnittet "
                   "**Ljud** i backend/README.md och välj en ny version av distributionen.")

    st.markdown("**Röster**")
    spanish = "es-MX"
    if any((language_tag(v["language"]) or "").lower().startswith("es") for v in lists):
        spanish = st.selectbox("Spansk språkvariant", ["es-MX", "es-CL"],
                               format_func=lambda x: "Latinamerikansk spanska (Mexiko)" if x == "es-MX" else "Chilensk spanska",
                               key="audio_accent")
    languages = sorted({voice_language(v, spanish) for v in lists} - {None}) + ["sv-SE"]
    voices = {}
    columns = st.columns(len(dict.fromkeys(languages)))
    for column, language in zip(columns, dict.fromkeys(languages)):
        with column:
            options = VOICES[language]
            voices[language] = st.selectbox(f"Röst för {LANGUAGE_NAMES.get(language[:2], language)}", list(options),
                                            format_func=options.get, key="voice_" + language)
            if st.button("Provlyssna", key="preview_" + language, disabled=not configured, icon=":material/volume_up:"):
                sample = next((w["svenska"] if language == "sv-SE" else w["accepted_answers"][0]
                               for v in lists if language == "sv-SE" or voice_language(v, spanish) == language
                               for w in v["words"][:1]), "Hej")
                try:
                    _, clip = make_clip(sample, language, voices[language], key, region)
                    st.audio(base64.b64decode(clip["mp3"]), format="audio/mp3")
                except ServiceError as error:
                    st.error(str(error))
    unsupported = sorted({v["language"] for v in lists if not voice_language(v, spanish)})
    if unsupported:
        st.caption("AI-röster finns ännu inte för: " + ", ".join(unsupported) + ". De listorna använder enhetens röst.")

    st.markdown("**Skapa ljud**")
    scope = st.radio("Skapa ljud för", ["Alla listor", "En lista"], horizontal=True, key="audio_scope")
    chosen = lists
    if scope == "En lista":
        selected = st.selectbox("Gloslista", [v["id"] for v in lists],
                                format_func=lambda i: next(v["name"] for v in lists if v["id"] == i), key="audio_list")
        chosen = [v for v in lists if v["id"] == selected]
    requests = needed(chosen, voices, spanish)
    have = {**load_bank()["clips"], **stored}
    missing = [r for r in requests if have.get(clip_key(r[0], r[1]), {}).get("voice") != r[2]]
    st.caption(f"{len(requests) - len(missing)} av {len(requests)} uttryck har redan AI-röst. {len(missing)} saknas.")
    if missing:
        minutes = max(1, math.ceil(len(missing) * 3.2 / 60))
        st.caption(f"Det tar ungefär {minutes} min. Håll fliken öppen. Avbryts det sparas det som hunnit skapas, "
                   "och du fortsätter där du slutade genom att klicka igen.")
    label = f"Skapa {len(missing)} ljud" if missing else "Alla ljud är klara"
    if st.button(label, type="primary", disabled=not (configured and storage_ok and missing)):
        bar = st.progress(0.0, text="Skapar ljud …")
        try:
            generate(missing, key, region, lambda batch: db.save_audio(token, batch),
                     on_progress=lambda done, total: bar.progress(done / total, text=f"{done} av {total} ljud klara"))
        except ServiceError as error:
            st.error(str(error))
            st.caption("Ljuden som hann skapas är sparade. Klicka igen för att fortsätta.")
        else:
            bar.progress(1.0, text="Klart!")
            st.success("Ljuden är sparade. Eleverna hör de nya rösterna nästa gång de lyssnar.")
        finally:
            saved_clips.clear()
