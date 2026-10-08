# Google Sheets för GlosFlow 2

V2 har en ny backend. **Byt inte ut din gamla backend innan du har säkerhetskopierat och verifierat den nya versionen.** Använd ett separat kalkylblad och ett separat Apps Script-projekt.

## Uppdatering av en befintlig GlosFlow 2-backend

För namn/PIN-inloggning: ersätt Code.gs i det befintliga Apps Script-projektet och välj Distribuera → Hantera distributioner → aktiv distribution → pennan → Version: Ny version → Distribuera. Behåll samma kalkylblad och Script Properties, inklusive PIN_PEPPER. Se ../UPPDATERING.md för hela arbetsgången. Detta kräver inget nytt kalkylblad när du redan använder v2-tabellerna.

`authenticate_student` tar namn och PIN, söker exakt en matchning och returnerar samma elev-ID, klass och tokenformat som tidigare. `authenticate` med klass finns kvar för förnyelse av en redan identifierad session. Båda anropen delar spärren per elevnamn. Nya konton kan inte dela både namn och PIN-kod; äldre dubbla kombinationer avvisas vid namn/PIN-inloggning.

## Installation från en äldre version

1. Skapa ett nytt, privat Google-kalkylblad. Kopiera kalkylbladets ID från adressen mellan `/d/` och `/edit`.
2. Öppna Tillägg → Apps Script. Ersätt innehållet i `Code.gs` med projektets [Code.gs](Code.gs).
3. Öppna projektinställningarna och lägg till dessa Script Properties:

| Namn | Värde |
| --- | --- |
| `SPREADSHEET_ID` | ID för det nya kalkylbladet. |
| `API_KEY` | Minst 32 slumpmässiga tecken. Samma värde blir `GSHEETS_API_KEY` i Streamlit. |
| `PIN_PEPPER` | En annan hemlighet med minst 32 slumpmässiga tecken. Behåll den; att byta den gör tidigare PIN-koder ogiltiga. |
| `ADMIN_PASSWORD` | Ditt eget lärarlösenord, minst 12 tecken. |

Skapa två olika hemligheter lokalt, exempelvis genom att köra följande två gånger. Klistra bara in resultatet i respektive hemlighetsinställning.

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

4. Välj Distribuera → Ny distribution → Webbapp. Kör som dig själv. För åtkomst väljer du det alternativ som låter den serverbaserade Streamlit-appen anropa webbappen utan Google-inloggning, vanligtvis ”Alla”. **Alla anrop kräver fortfarande den hemliga API-nyckeln**; det finns inget offentligt `get_users`-anrop. Om skolans Workspace-policy förbjuder denna typ av webbapp behöver du använda en egen server med SQLite eller ordna en godkänd backend med skolans IT.
5. Godkänn de behörigheter Google begär och kopiera distributionens adress som slutar på `/exec`. Använd inte `/dev`.
6. Ange `BACKEND`, `GSHEETS_URL` och `GSHEETS_API_KEY` i Streamlit enligt huvudguiden. Publicera inga hemligheter i repositoryt. `ADMIN_PASSWORD` i Streamlit används endast av SQLite-alternativet; med Sheets kontrolleras det av Apps Script.
7. Logga in som lärare och skapa ett testkonto. De nya tabellerna `Users_v2`, `Sessions_v2`, `Failures_v2` och `Lists_v2` skapas automatiskt vid användning.

Vid kodändringar i Apps Script: uppdatera distributionen till en ny version, annars kör `/exec` fortfarande den tidigare versionen.

## Driftkontroll

- Träna ett ord, logga ut, logga in igen och kontrollera samma lådor.
- Öppna två elevflikar innan något svar har sparats. Svara i den första, därefter i den andra. Den andra ska visa en konflikt och inte skriva över första svaret.
- Prova ett fel och kontrollera att glosan flyttas till rött och återkommer i omgången.
- Prova en ledtråd och kontrollera att svaret inte flyttar ordet framåt.
- Skapa en lista med två ord och kontrollera quizet. Appen lägger inte in främmande utfyllnadsalternativ.
- Kontrollera att lärare kan se elever och att eleven saknar åtkomst till lärarpanelen.

## Säkerhet och sparning

API-nyckeln skickas från Streamlit-servern i POST-kroppen, aldrig i adressen eller till elevens webbläsare. Eleven får bara sin egen sessionstoken och progression. PIN-koder lagras som en saltad HMAC-SHA256 med separat serverhemlighet; enbart kalkylbladsinnehållet räcker inte för att pröva PIN-koder offline. Kalkylblad och Script Properties ska vara privata. Sessioner lagras som hashade tokens och löper ut efter åtta timmar. Inloggning spärras efter fem fel i 15 minuter per elevnamn (lärarinloggningen har en separat spärr).

Fyra siffror är ett enkelt klassrumsinlogg, inte stark autentisering för känslig information. Använd endast namn/alias, klass och övningsdata som behövs för verktyget. Undvik annan elevinformation. Dela inte kalkylbladet med elever. Exportfiler med elevprogression hanteras som privata säkerhetskopior.

Alla backendåtgärder kräver API-nyckel. Läraråtgärder kräver dessutom en lärarsession. Progression hämtas för tokenens konto, aldrig för ett användarnamn i en sparbegäran. Skrivningar låses med ScriptLock, och revision, operations-ID och progression skrivs tillsammans. En gammal revision avvisas. Progression delas över flera celler för att klara många glosor.

Google Sheets är en enkel backend för en mindre skolpilot och har tjänstekvoter. Den är inte avsedd för stor publik trafik. Backendens kontrakt har testats med testdubblar; dessa verifierar inte Googles verkliga nätverk, behörigheter eller kvoter.

## Tidigare data

Den gamla databasens schema och Apps Script ingick inte i underlaget. Denna backend gör inga automatiska ändringar i dem. Exportera gamla lådor separat. Lärarpanelen kan importera en elevs gamla `leitner`-dictionary till ett nyskapat konto. Spara den gamla databasen och exporten tills du kontrollerat resultatet.
