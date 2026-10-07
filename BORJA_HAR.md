# Uppdatera din befintliga app

Detta paket är anpassat till `patrickljungblad/voc-guide` och startfilen `glostranare_web-v4.py`.

Du kan göra uppladdningen helt i webbläsaren. Streamlit installerar programmets paket på sin server; du behöver inte installera Python på datorn.

## 1. Packa upp

1. Ladda ner den uppdaterade ZIP-filen och dubbelklicka på den.
2. Öppna den uppackade mappen. Där ska du direkt se `glostranare_web-v4.py`, `requirements.txt`, `BORJA_HAR.md` och mappar som `core`, `data` och `ui`.
3. På Mac: tryck Command + Shift + punkt för att även visa mapparna `.streamlit` och `.github` samt filen `.gitignore`.

## 2. Ladda upp till GitHub

1. Öppna https://github.com/patrickljungblad/voc-guide och välj fliken Code.
2. Kontrollera att grenen som visas är `main`.
3. Välj Add file → Upload files.
4. Dra alla filer och undermappar **inifrån** den uppackade mappen till uppladdningsrutan. Dra inte själva yttersta mappen: filerna ska hamna direkt i repositoryts rot.
5. I uppladdningslistan ska du se `glostranare_web-v4.py`, `requirements.txt` och exempelvis `core/leitner.py`. Om allt börjar med ett extra mappnamn, avbryt och dra innehållet i mappen i stället.
6. Skriv `Uppdatera till GlosFlow 2` i meddelanderutan.
7. Välj Commit directly to the main branch och klicka Commit changes. Detta publicerar kodändringen till grenen som din app använder.

GitHub ersätter filerna med samma namn och lägger till de nya mapparna. Din befintliga `.devcontainer` ingår inte i paketet och behöver ingen ändring.

## 3. Öppna appen

Öppna din vanliga Streamlit-adress efter att ändringen har sparats. Den nya versionen ska starta från samma `glostranare_web-v4.py`. Första omstarten kan ta lite tid medan paketen installeras.

Välj **Prova som gäst** för att kontrollera gränssnitt och glosträning.

Om appen visar ett fel: kopiera felmeddelandet eller skicka en bild av det. Felmeddelandet hjälper till att avgöra om det gäller uppladdning, Python-version eller konfiguration.

## 4. Koppla beständig sparning

Den gamla Google Sheets-backenden använder ett annat kontrakt. Gamla elevkonton börjar därför inte fungera automatiskt med den nya versionen. Som standard kan appen provköras med gästläge och lokal SQLite; molnserverns lokala databas ska inte användas för beständig elevdata.

Följ `backend/README.md` för att skapa den nya backendkopplingen i ett separat Google-kalkylblad. Den guiden visar vilka fyra inställningar som behövs i Apps Script.

När den nya backendkopplingen är skapad, gå till https://share.streamlit.io, öppna menyn med tre punkter för din app, välj Settings och sedan Secrets. Ange följande där med dina verkliga värden:

```toml
BACKEND = "gsheets"
GSHEETS_URL = "https://script.google.com/macros/s/DIN_NYA_DEPLOYMENT/exec"
GSHEETS_API_KEY = "DIN_HEMLIGA_API_NYCKEL"
```

Om `GSHEETS_URL` redan finns i inställningarna: ersätt dess gamla värde med den nya adressen; skriv inte samma nyckel två gånger. Andra orelaterade inställningar kan finnas kvar. Lägg inga hemligheter i repositoryt.

Logga sedan in som lärare, skapa ett testkonto och kontrollera att elevens lådor finns kvar efter utloggning och ny inloggning. För tidigare elevframsteg finns en separat importfunktion i lärarpanelen.
