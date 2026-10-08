import json
import streamlit as st
from services.config import setting
from services.database import ServiceError
from services.speech import VOICES, load_bank, get_or_create, clip_key, store_clips
from ui.audio import language_tag


def speech_panel(lists):
    st.subheader("Naturligare uppläsning")
    st.caption("Provlyssna, välj röster och skapa ljudfiler till en lista. Eleverna spelar upp sparat ljud; inga nya ljud skapas när de lyssnar.")
    key = setting("AZURE_SPEECH_KEY")
    region = setting("AZURE_SPEECH_REGION")
    configured = bool(key and region)
    if not configured:
        st.info("För att skapa och provlyssna på naturliga AI-röster behöver du lägga in AZURE_SPEECH_KEY och AZURE_SPEECH_REGION under Settings → Secrets i Streamlit. Under tiden används den bästa rösten som finns på elevens enhet.")
    selected = st.selectbox("Gloslista för ljud", [v["id"] for v in lists],
                            format_func=lambda i: next(v["name"] for v in lists if v["id"] == i), key="audio_list")
    vocab = next(v for v in lists if v["id"] == selected)
    tag = language_tag(vocab["language"])
    if tag and tag.lower().startswith("es"):
        accent = st.selectbox("Spansk språkvariant", ["es-MX", "es-CL"], format_func=lambda x: "Latinamerikansk spanska (Mexiko)" if x == "es-MX" else "Chilensk spanska", key="audio_accent")
    else:
        accent = tag
    if accent not in VOICES:
        st.info("Ljudskapande är förberett för spanska, svenska och brittisk engelska. Listans befintliga webbläsarröst används för andra språk.")
        return
    voices = VOICES[accent]
    target_voice = st.selectbox("Röst på målspråket", list(voices), format_func=voices.get, key="target_voice_" + accent)
    swedish_voice = st.selectbox("Svensk röst", list(VOICES["sv-SE"]), format_func=VOICES["sv-SE"].get, key="swedish_voice")
    sample = vocab["words"][0]
    left, right = st.columns(2)
    for column, text, language, voice, label in (
        (left, sample["accepted_answers"][0], accent, target_voice, "Provlyssna på målspråket"),
        (right, sample["svenska"], "sv-SE", swedish_voice, "Provlyssna på svenska"),
    ):
        with column:
            if st.button(label, disabled=not configured):
                try:
                    st.audio(get_or_create(text, language, voice, key, region), format="audio/mp3")
                except ServiceError as error:
                    st.error(str(error))
    requests = list(dict.fromkeys((text, lang, voice) for w in vocab["words"]
                    for texts, lang, voice in ((w["accepted_answers"], accent, target_voice), ([w["svenska"], *w["swedish_answers"]], "sv-SE", swedish_voice)) for text in texts))
    bank = load_bank()
    missing = [(text, lang, voice) for text, lang, voice in requests if bank["clips"].get(clip_key(text, lang), {}).get("voice") != voice]
    st.caption(f"{len(requests) - len(missing)} av {len(requests)} uttryck finns med de valda rösterna. {len(missing)} behöver skapas.")
    confirmed = st.checkbox("Jag har provlyssnat och vill använda dessa röster", key="voices_confirmed_" + selected + target_voice + swedish_voice)
    st.caption("Ljudtjänsten kan ta betalt för ljudskapandet enligt ditt abonnemang. Långsamt tempo återanvänder samma ljudfil.")
    if st.button("Skapa saknade ljud för listan" if missing else "Aktivera de valda rösterna", disabled=not configured or not confirmed, type="primary"):
        progress = st.progress(0, text="Skapar ljud …")
        try:
            for i, (text, lang, voice) in enumerate(missing):
                get_or_create(text, lang, voice, key, region)
                progress.progress((i+1)/len(missing), text=f"{i+1} av {len(missing)} ljud klara")
            store_clips({}, {"es": accent} if accent.startswith("es") else {})
            progress.progress(1, text="Ljuden är klara")
            st.success("Ljuden är klara och används nu vid nästa öppning av listan. Ladda ner ljudbiblioteket nedan för att behålla dem efter omstart.")
        except ServiceError as error:
            st.error(str(error))
            st.caption("Färdiga ljud har sparats. Knappen fortsätter med de saknade ljuden vid nästa försök.")
        bank = load_bank()
    if bank["clips"]:
        st.download_button("Ladda ner ljudbibliotek", json.dumps(bank, ensure_ascii=False).encode("utf-8"), "audio_bank.json", "application/json")
        st.caption("För beständig lagring: ladda upp audio_bank.json i GitHubs data-mapp och starta om Streamlit. Filen innehåller ljud och röstnamn, inga nycklar.")
