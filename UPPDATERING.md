# Flow-logga, tydliga framsteg och enklare inloggning

Detta kompletta paket innehåller även tidigare förbättringar: delbara listor, träning utan konto, temabilder, PDF-förhör och stöd för sparade ljud.

## Vad som ändrats

- Ny Flow-logga med böljande blågröna band och ett blad, som i det valda förslaget 1. Loggan är en SVG och håller sig skarp på både dator och mobil.
- **Öva. Minns. Se dina framsteg.** står i välkomstrutan. Slogantexten har tagits bort från loggan.
- Knappen heter **Öva på dessa glosor**.
- Under övningens rubrik finns en liten framstegsrad: **Ska övas · På väg · Kan bra**, med antal och en tunn färgmätare. Den gäller hela gloslistan i den riktning eleven tränar och uppdateras direkt efter rättning. **Fråga X av Y** beskriver fortfarande själva omgången.
- Elevinloggningen har endast **Namn** och **PIN-kod**. Klass används fortfarande i lärarens konto- och elevöversikt, men eleven behöver inte fylla i den.

## 1. Uppdatera Google Apps Script först

Detta steg behövs för inloggning utan klass. Att ladda upp Code.gs på GitHub ändrar inte koden som Google kör.

1. Öppna ditt **befintliga** Google-kalkylblad för GlosFlow och välj **Tillägg → Apps Script**.
2. Öppna **Code.gs** i det projekt som din app redan använder. Kopiera gärna den nuvarande koden till en lokal textfil före bytet.
3. Öppna paketets **backend/Code.gs** i en textredigerare. Kopiera hela innehållet och ersätt innehållet i Apps Scripts **Code.gs**. Spara.
4. Välj **Distribuera → Hantera distributioner** (*Deploy → Manage deployments*).
5. Välj den aktiva webbappdistributionen och klicka på **pennan** (*Edit*).
6. Under **Version** väljer du **Ny version** (*New version*). Klicka på **Distribuera** (*Deploy*).

Behåll samma kalkylblad, distribution, åtkomstinställningar och Script Properties. Den uppdaterade befintliga distributionen behåller samma /exec-adress, så Streamlit Secrets behöver inte ändras. Konton, elev-ID, sparade framsteg och gloslistor använder samma tabeller som tidigare.

Googles instruktioner: https://developers.google.com/apps-script/concepts/deployments#edit_a_versioned_deployment

## 2. Ladda upp uppdaterade filer på GitHub

Packa upp ZIP-filen i en **ny mapp** på din Mac. Öppna först rätt mapp på GitHub. Välj **Add file → Upload files → choose your files**, markera filerna med **⌘ Command** och spara med **Commit changes** på **main**.

| Öppna på GitHub | Filer att välja i paketet |
| --- | --- |
| `services` | `database.py`, `gsheets.py` |
| `ui` | `glosflow-logo.svg`, `style.py`, `visuals.py`, `training.py`, `login.py`, `list_page.py` |
| `backend` | `Code.gs`, `README.md` |
| `tests` | `test_app.py`, `test_database.py`, `backend.test.cjs` |
| Repositoryts startsida | `requirements.txt`, `requirements-dev.txt`, `UPPDATERING.md`, `README.md`, `BORJA_HAR.md` |

Direktlänkar:

- https://github.com/patrickljungblad/voc-guide/tree/main/services
- https://github.com/patrickljungblad/voc-guide/tree/main/ui
- https://github.com/patrickljungblad/voc-guide/tree/main/backend
- https://github.com/patrickljungblad/voc-guide/tree/main/tests
- https://github.com/patrickljungblad/voc-guide

Ladda upp services före ui, så att det nya inloggningsanropet finns innan formuläret används. Du behöver inte ladda upp startfilen eller dolda mappar för den här uppdateringen.

`requirements.txt` innehåller fortfarande `reportlab>=4.2,<5`, som PDF-förhören kräver. Ladda upp den så att även den tidigare saknade PDF-installationen är med.

## 3. Starta om och kontrollera

Välj **Reboot** för appen på https://share.streamlit.io och öppna sedan appen igen.

1. Startsidan visar Flow-loggan utan slogan bredvid. Välkomstrutan visar den flyttade sloganen.
2. Välj kurs och öppna en lista. Knappen heter **Öva på dessa glosor**.
3. Starta en omgång. Den lilla raden under rubriken visar alla ord i listan, inte bara orden i omgången.
4. Svara rätt utan hjälp på ett nytt ord. Det flyttas från **Ska övas** till **På väg**, och raden ändras direkt. Att gå vidare eller ladda om frågan räknar inte svaret en gång till.
5. Logga in med ett befintligt testkontos **namn och PIN-kod**, utan klass. Kontrollera att kontots tidigare framsteg hämtas och att nya svar finns kvar efter ut- och inloggning.
6. Kontrollera gärna PDF-förhör och en delad gloslistelänk också.

Om elevinloggningen säger att Google Apps Script behöver uppdateras kör /exec fortfarande den gamla versionen. Kontrollera steg 1, särskilt **Ny version** i den befintliga distributionen.

## Konton med samma namn

Elever får ha samma namn i olika klasser om de har **olika PIN-koder**. Inloggningen väljer endast när precis ett konto matchar både namn och PIN-kod. Nya konton med en redan använd namn/PIN-kombination avvisas med en förklaring till läraren. Äldre dubbla kombinationer väljs inte på måfå; de behöver skiljas åt av läraren. Felaktiga försök spärras efter fem försök i 15 minuter per elevnamn.

## Ljud och befintliga data

Läs **LJUD.md** för den tidigare funktionen med naturligare röster. Den här uppdateringen genererar inga nya ljud. Behåll ett befintligt `data/audio_bank.json` som du själv fyllt med ljud; paketets tomma exempel ska inte ersätta det.

## Testning

Automatiska tester kontrollerar bland annat inloggning och kontoval, avvisning av dubbla namn/PIN-kombinationer, spärrade försök, sparade framsteg och den direkta framstegsvisningen. Google-backenden testas med ett Apps Script/Sheets-teststöd, inte mot ditt verkliga kalkylblad. Dator- och mobilvyn granskas i en lokal webbläsare.
