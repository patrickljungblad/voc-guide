# Delbara gloslistor och lyssna

## Senaste tillägget: ny GlosFlow-logga

Loggan använder samma blå–gröna färger som tidigare, med ett stiliserat G och ett blad. Den anpassar sig till skärmens bredd och finns i `ui/glosflow-logo.svg`.

**Har du redan lagt in uppdateringen med delbara listor och lyssna?** Då räcker det att ladda upp hela mappen `ui` från detta paket via **Add file → Upload files** i repositoryts rot. Klicka **Commit changes**. Det är `ui/style.py` och `ui/glosflow-logo.svg` som behövs för loggbytet, och båda måste följa med. Ladda inte upp ZIP-filen direkt.

Om du ännu inte lagt in förra uppdateringen, följ hela uppladdningen nedan.

Den här uppdateringen använder din befintliga Streamlit-app och Google Sheets-koppling. Du behöver inte installera något på din dator eller ändra Secrets eller Apps Script.

## Ladda upp ändringen

1. Packa upp `GlosFlow-2.zip`.
2. Öppna https://github.com/patrickljungblad/voc-guide på grenen `main`.
3. Välj **Add file → Upload files** från repositoryts rot.
4. Dra in dessa tre saker från den uppackade mappen:
   - filen `glostranare_web-v4.py`
   - hela mappen `ui`
   - hela mappen `core`
5. Kontrollera att uppladdningen visar exempelvis `ui/speech.html` och `core/trainer.py`. Det ska inte stå en extra yttersta mapp före filnamnen.
6. Skriv `Delbara gloslistor och lyssna` och klicka **Commit changes**.
7. Öppna din vanliga appadress när Streamlit har läst in ändringen.

De tre delarna behöver laddas upp tillsammans. Mappen `ui` innehåller nya filer som behövs för uppläsning och listvisning. Om du arbetar med Git i stället kan du uppdatera hela paketets innehåll, inklusive tester och dokumentation.

## Kontrollera

- Öppna appen i ett privat webbläsarfönster. Glosbiblioteket ska visas direkt utan inloggning.
- Öppna en lista. Alla glosor finns under övningsknappen, med uppläsning på svenska och målspråket.
- Under **Dela gloslistan** finns en länk med `?lista=...`. Kopiera den och öppna den i ett nytt privat fönster: samma lista ska visas.
- Tryck **Öva denna lista** och därefter **Fortsätt träna**. Quiz, skrivträning och ordkort fungerar utan konto.
- Välj **Logga in för att spara framsteg** när du vill använda ett befintligt elevkonto. Det hämtar kontots sparade framsteg; tidigare gästträning förs inte över. Läraren skapar fortfarande konton.
- Logga in som lärare via samma knapp. Länken för vald lista finns även i lärarpanelen.

## Lyssna

Välj Normalt eller Långsamt och tryck 🔊 vid ordet. Det går även att lyssna efter rättning och när ett ordkort är vänt. Under en fråga kan eleven välja **Lyssna på svaret som hjälp**. Då markeras svaret som hjälpt och flyttar inte ordet framåt.

Uppläsningen använder röster på elevens enhet. En latinamerikansk spansk röst prioriteras om en sådan finns. Annars används en annan tillgänglig spansk röst. Om rätt språk saknas visas en förklaring, medan glosträningen fortfarande fungerar. Prova en annan webbläsare eller aktivera en röst för språket på enheten. På mobilen: kontrollera ljudvolymen.

Ingen inspelning, automatisk uttalsbedömning eller egen kontoregistrering ingår i denna uppdatering.

Alla gloslistor kan läsas av den som kommer åt appen. Elevkonton och sparade framsteg kräver fortfarande inloggning. Om själva Streamlit-appen har begränsad åtkomst gäller den även för delade länkar.
