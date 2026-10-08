# GlosFlow 2

**För ditt befintliga repository `patrickljungblad/voc-guide`: börja med [BORJA_HAR.md](BORJA_HAR.md). Paketet använder startfilen `glostranare_web-v4.py`.**

**Har du redan installerat GlosFlow 2? Följ [UPPDATERING.md](UPPDATERING.md) för tydligare kursval, temabilder, PDF-glosförhör och stöd för bättre ljud. Guiden visar individuell filuppladdning på Mac.**

Ett lugnt, webbaserat glosverktyg för elever: öppna en delad gloslista, lyssna, öva och se hur orden flyttar mellan tre Leitner-lådor. Byggt med Streamlit och Python 3.12. Inget konto behövs för att se glosor eller öva. Befintliga elevkonton används för beständig sparning.

Logotypen i `ui/glosflow-logo.svg` är den valda Flow-loggan: ett böljande blågrönt G med band, blad och GlosFlow-text. Slogantexten visas i startsidans välkomstruta. Sidhuvudet läser in den som en data-URI, så ingen separat bildserver behövs. Behåll SVG-filen tillsammans med `ui/style.py` vid uppladdning.

Biblioteket har illustrerade gloskort, två kolumner på dator och en på mobil. Under en övning visas svarsalternativ som tydliga kort och repetitionsinformation och hjälp ligger i paneler. En avslutad omgång visar olika glosor som faktiskt tränats, antal rätt och hur många tränade ord som ligger i Ska övas. Korta animationer respekterar enhetens önskemål om minskad rörelse. Illustrationerna i `ui/visuals.py` är lokala SVG-former och gör inga externa bildanrop. Ingen ny poängmodell eller ändring av sparningsreglerna ingår.

## Gloslistor och uppläsning

Varje lista har en delbar adress med sitt stabila ID: `?lista=LIST_ID`. Öppna listan och kopiera adressen under **Dela gloslistan**, eller använd länken i lärarpanelen. Eleven ser glosorna direkt och väljer **Öva på dessa glosor**. Alla listor är synliga för den som kommer åt appen; elevdata kräver inloggning. Appens eventuella åtkomstbegränsning i Streamlit gäller även delade länkar.

Glosor på svenska och målspråket kan läsas upp i normal eller långsam takt. Läraren kan provlyssna och skapa naturligare ljud med Azure Speech under **Röster och ljud**. Det kräver eget tjänstekonto och nyckel hos Azure. Skapade ljud återanvänds utan API-anrop vid elevens uppspelning. Ladda ner audio_bank.json och spara i data-mappen på GitHub för beständig lagring. För ord utan sparat ljud används webbläsarens Speech Synthesis API; en latinamerikansk spansk röst prioriteras. Tillgänglighet och röst varierar mellan enheter.

Biblioteket börjar med ett större **Välj kurs** utan förvalt alternativ. Valet behålls när eleven går tillbaka till biblioteket. Temabilder föreslås från listans namn och ord. Alla åtta ursprungliga listor har matchande motiv, och läraren kan välja en annan temabild vid redigering.

Lärarpanelens **Glosförhör** skapar vanliga översättningsförhör som A4-PDF med separat facit. Välj riktning, alla glosor eller ett urval, blandad ordning och A/B-versioner med samma glosor i olika ordning. Facit visar listans godkända svarsalternativ och följer respektive version.

Det går att lyssna efter rättning, på vända ordkort och som uttrycklig hjälp under en fråga. Hjälp genom uppläsning ger inget avancemang och ordet upprepas i omgången. Gästträning bevaras i webbsessionen. Vid inloggning hämtas kontots sparade framsteg och aktuell gästomgång avslutas; gästframsteg förs inte över. Egen kontoregistrering och inspelad uttalsövning ingår ännu inte.

## Kom igång på din dator

Packa upp projektet och öppna en terminal i mappen som innehåller `glostranare_web-v4.py`.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run glostranare_web-v4.py
```

På Windows: aktivera med `.venv\Scripts\activate` i stället. Gästläget fungerar direkt. För lärarpanelen, kopiera `.streamlit/secrets.example.toml` till `.streamlit/secrets.toml` och sätt ett eget långt `ADMIN_PASSWORD` (minst 12 tecken rekommenderas). Skapa sedan elevkonton från lärarpanelen.

Lokal utveckling använder SQLite i `runtime/`. Spara och säkerhetskopiera denna mapp om du driver appen på egen server med beständig disk. Den följer inte med till GitHub. Elevkonton sparas med saltade scrypt-hashar för PIN-koder; fem misslyckade inloggningar ger 15 minuters spärr för kontot.

## Till GitHub

1. Skapa ett nytt, tomt repository på GitHub.
2. Ladda upp **innehållet i projektmappen**, så att `glostranare_web-v4.py` och `requirements.txt` hamnar i repositoryts rot. Ta med `.streamlit/config.toml` och `.github/workflows/tests.yml`.
3. Lägg aldrig upp `secrets.toml`, `runtime/`, elevexporter eller den gamla kodfilen med sin inbyggda backendadress. `.gitignore` skyddar dessa vid vanlig Git-användning; vid manuell uppladdning behöver du välja rätt filer själv.

Alternativt, med Git installerat:

```bash
git init
git add .
git commit -m "GlosFlow 2: spaced repetition and persistent progress"
git branch -M main
git remote add origin https://github.com/DITT_KONTO/glosflow.git
git push -u origin main
```

Projektet innehåller GitHub Actions som kör Python- och backendtester vid push och pull request.

## Publicera som fungerande webbapp

GitHub lagrar koden. GitHub Pages kan inte köra en Python/Streamlit-app. För denna version används till exempel Streamlit Community Cloud eller en egen Python-server.

För Streamlit Cloud:

1. Följ [backend/README.md](backend/README.md) och konfigurera den nya Google Sheets-backenden.
2. Skapa en app från ditt GitHub-repository och välj `glostranare_web-v4.py` som startfil och Python 3.12.
3. Ange följande i appens Secrets-inställningar:

```toml
BACKEND = "gsheets"
GSHEETS_URL = "https://script.google.com/macros/s/DIN_DEPLOYMENT/exec"
GSHEETS_API_KEY = "DIN_SLUMPMÄSSIGA_HEMLIGHET"
```

4. Logga in som lärare, skapa ett testkonto, träna några ord, logga ut och in igen och kontrollera lådorna. Prova även två öppna flikar. Testa med egna testkonton innan du tar in elever.

Använd Google Sheets eller annan beständig lagring på en molnplattform som inte garanterar beständig lokal disk. Konfigurationsfel ger ett tydligt fel; appen faller inte tyst tillbaka till en annan databas.

## Hur lärandet fungerar

| Låda | Vad händer? |
| --- | --- |
| 🔴 Ska övas | Nya ord och ord som har besvarats fel i På väg. Ett korrekt quiz- eller skrivsvar utan hjälp flyttar ordet till På väg. |
| 🟡 På väg | Repetition efter tre dagar. För att nå Kan bra krävs ett skrivsvar utan hjälp när ordet är redo att repeteras. |
| 🟢 Kan bra | Kontrolleras efter sju dagar. Ett fel flyttar ordet ett steg ner, till På väg. |

Efter ett fel är ordet redo igen efter tio minuter och kommer dessutom tillbaka efter upp till tre andra ord i den aktuella omgången. Det senare är stödjande övning och räknas inte som ett nytt självständigt minnesbevis. Listor med få ord ger kortare mellanrum. Ett ord läggs tillbaka högst en gång per omgång och omgången har ett tak på 20 frågor.

Ordkort har två självbedömningsknappar. "Behöver öva" flyttar ordet ett steg ner, men korten flyttar aldrig ord framåt. Ett korrekt självbedömt kort i rött schemaläggs till nästa dag. Ett hjälpberoende svar ger ny repetition efter tio minuter om ordet var redo. Extra övning före repetitionsdatumet flyttar inte ordet framåt eller skjuter upp nästa planerade repetition.

Minnestips och bokstavsledtrådar markerar svaret som hjälpt. ”Nästan rätt” behåller lådan och ger kortare väntan till nästa repetition. Saknad akut accent och mindre stavfel kan ge ”nästan rätt”, men aldrig godkänt svar eller avancemang. Egna bokstäver som ñ, å, ä och ö tas inte bort vid rättning. Versaler, extra mellanrum och frågetecken runt svaret ignoreras.

De två översättningsriktningarna har **separata framsteg**. Svenska → spanska säger något annat om elevens minne än spanska → svenska.

## Innehåll och lärarpanel

Alla åtta ursprungliga listor med totalt 125 glosor följer med. List- och ord-ID är stabila och lagrade i JSON. Att byta namn på en lista raderar inte framstegen. Några tydliga stavfel är rättade (`teléfono`, `adiós`) och alternativ som `computadora`/`ordenador` godkänns var för sig. Den ursprungliga formen `tenéis` finns kvar.

Läraren kan skapa listor genom att klistra in två tabbseparerade kolumner från ett kalkylblad. Använd `|` mellan alternativa svar. En tredje kolumn kan innehålla ett minnestips. Listor kan ändras i en tabell, exporteras och importeras som JSON. En redan öppen webbsession behåller sin listkopia; öppna ett nytt besök eller logga ut för att hämta senaste versionen.

Ändra befintliga ord för att rätta stavning eller lägga till en alternativ översättning. Om betydelsen ändras: skapa en ny rad och ta bort den gamla så att glosan får ett nytt ID. Försök inte återanvända ett gammalt ID för ett annat ord.

Lärarpanelen visar lådorna för vald lista och kan exportera elevframsteg för säkerhetskopiering. Använd lådorna som stöd för övning, inte som betyg eller jämförelse mellan elever. Minnestips är granskbara och lagrade i listan; inga AI-anrop görs under elevens träning.

## Befintliga elever och data

Den tidigare backendkoden och själva elevdatabasen ingick inte i underlaget. V2 använder därför ett nytt backendkontrakt; den gamla Apps Script-adressen fungerar inte direkt med denna version.

Behåll originalapp och kalkylblad tills flytten är verifierad. Skapa elevkonton på nytt och välj nya PIN-koder. Om du kan exportera den gamla elevens `leitner`-dictionary som JSON kan lärarpanelen importera lådorna. Importen matchar gamla namnnycklar via en fast `legacy_key` och ignorerar gamla statistikfält. Nya framsteg skrivs inte över av importen. Importerade ord blir redo för kontroll direkt, samtidigt som deras lådnummer bevaras. Okända eller dubblerade gamla nycklar kan inte återskapas säkert; spara originalexporten.

Ingen kod i detta projekt skriver till din tidigare databas eller flyttar verkliga elevdata automatiskt.

## Sparning och återhämtning

Ett bedömt svar ändrar progressionen en gång. Rättningen visas före nätverksanropet till databasen, så eleven får återkoppling medan framstegen sparas. Nästa ord öppnas när sparningen är klar. Varje snapshot har en förväntad revision och ett operations-ID. Backend serialiserar skrivningar och avvisar en för gammal revision. Ett nytt försök att spara samma operation är säkert även om nätverksanropet hann slutföras innan svaret försvann.

Vid nätverksfel behålls svaret i sessionen. Eleven kan försöka spara igen eller hämta en JSON-kopia. Vid konflikt behöver eleven hämta den sparade versionen; en lokal kopia erbjuds först. Utgången inloggning kan förnyas med PIN utan att det osparade svaret raderas. Om hela webbsessionen försvinner innan sparning eller export går osparade svar förlorade.

Endast det uttryckliga ”Nollställ framsteg” raderar listans utveckling. Att öppna en lista, byta riktning eller starta en omgång raderar aldrig sparade lådor.

## Testa

```bash
pip install -r requirements-dev.txt
pytest -q
node --test tests/backend.test.cjs
```

Node 22 krävs bara för backendtesterna. Testerna kontrollerar lärandelogik, svarsrättning, återkommande felord, migration, autentisering, parallella sparningar, nätverksfel och interaktion genom Streamlits AppTest. Backendtesterna använder en testdubbel för Google-tjänsterna. En verklig Apps Script-deployment behöver fortfarande testas i ditt Google-konto efter konfiguration.

## Projektstruktur

- `glostranare_web-v4.py`: sidval och sessionsstart.
- `core/`: svarsrättning, Leitner, träningsomgångar och migration.
- `data/`: glosor och validering.
- `pedagogy/`: minnesstrategier.
- `services/`: konfiguration, SQLite och Google Sheets-klient.
- `ui/`: inloggning, bibliotek, träning och lärarpanel.
- `backend/`: den nya Google Apps Script-backenden och installationsguide.
- `tests/`: beteende- och regressionstester.

PDF-prov, XP, topplistor och live-AI ingår inte i denna kärnversion.

Dokumentation: [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest), [Google LockService](https://developers.google.com/apps-script/reference/lock/), [Script Properties](https://developers.google.com/apps-script/guides/properties).

## Inloggning med namn och PIN-kod

Eleven anger endast namn och PIN-kod. Klass finns kvar i lärarpanelen för att organisera konton. Samma namn kan finnas i flera klasser om PIN-koderna skiljer sig åt. Två konton med samma namn och PIN-kod får inte automatiskt väljas; nya sådana konton avvisas. Både nya och äldre inloggningsanrop delar spärren efter fem fel i 15 minuter per elevnamn. Befintliga konton och framsteg behåller sina ID. Uppdatera den befintliga Apps Script-distributionen enligt UPPDATERING.md för att aktivera elevinloggningen.

Under en pågående övning visas en diskret framstegsrad för hela gloslistan i vald språkriktning. Antalen ändras direkt vid rättning, innan eventuell fjärrsparning är klar. Omgångens frågenummer och svarsräknare gäller fortfarande bara omgången.
