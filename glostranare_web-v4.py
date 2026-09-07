function doPost(e) {
  var sheetApp = SpreadsheetApp.getActiveSpreadsheet();
  
  // Säkerställ att flikarna finns, annars skapas de automatiskt
  var statsSheet = sheetApp.getSheetByName("Statistik") || sheetApp.insertSheet("Statistik");
  var usersSheet = sheetApp.getSheetByName("Användare") || sheetApp.insertSheet("Användare");
  
  // Skapa rubriker om flikarna är helt tomma
  if (statsSheet.getLastRow() === 0) {
    statsSheet.appendRow(["Tidsstämpel", "Elevnamn", "Gloslista", "Rätt Svar", "Totala Försök", "Låda 1 (Röd)", "Låda 2 (Gul)", "Låda 3 (Grön)"]);
  }
  if (usersSheet.getLastRow() === 0) {
    usersSheet.appendRow(["Elevnamn", "PIN-kod", "Klass", "Leitner-Data", "Senast Sparad", "Score", "Total"]);
  }
  
  var data;
  try {
    data = JSON.parse(e.postData.contents);
  } catch(err) {
    return ContentService.createTextOutput(JSON.stringify({status: "error", message: "Ogiltig JSON: " + err.toString()})).setMimeType(ContentService.MimeType.JSON);
  }
  
  var action = data.action || "submit_result";
  
  // Säkerställda kolumn-index (namngivna variabler skyddar mot citat-stripping)
  var col_name = 0;
  var col_pin = 1;
  var col_group = 2;
  var col_leitner = 3;
  var col_saved = 4;
  var col_score = 5;
  var col_total = 6;
  
  // 1. SKICKA IN ENKELT LEKTIONSRESULTAT (FRÅN SIDOMENYN)
  if (action === "submit_result") {
    statsSheet.appendRow([
      data.timestamp || new Date().toISOString(),
      data.student,
      data.list_name,
      data.score,
      data.total,
      data.box1,
      data.box2,
      data.box3
    ]);
    return ContentService.createTextOutput(JSON.stringify({status: "success", action: "submit_result"})).setMimeType(ContentService.MimeType.JSON);
  }
  
  // 2. HÄMTA ALLA ELEVER OCH DERAS SPARADE PROGRESSION
  if (action === "get_users") {
    var rows = usersSheet.getDataRange().getValues();
    var users = [];
    for (var i = 1; i < rows.length; i++) {
      var row = rows[i];
      if (!row || !row[col_name]) continue; // Skippa tomma rader
      
      var leitnerObj = {};
      var rawLeitner = row[col_leitner];
      if (rawLeitner) {
        try {
          leitnerObj = JSON.parse(rawLeitner);
        } catch(err) {
          leitnerObj = {};
        }
      }
      
      users.push({
        name: row[col_name],
        pin: String(row[col_pin]),
        group: row[col_group],
        leitner: leitnerObj,
        last_saved: row[col_saved],
        score: Number(row[col_score]) || 0,
        total: Number(row[col_total]) || 0
      });
    }
    return ContentService.createTextOutput(JSON.stringify({status: "success", users: users})).setMimeType(ContentService.MimeType.JSON);
  }
  
  // 3. SKAPA ETT NYTT ELEVKONTO (FRÅN LÄRARPANELEN)
  if (action === "create_user") {
    var rows = usersSheet.getDataRange().getValues();
    var exists = false;
    for (var i = 1; i < rows.length; i++) {
      var row = rows[i];
      if (row && row[col_name] && row[col_name].toString().toLowerCase() === data.name.toString().toLowerCase()) {
        exists = true;
        break;
      }
    }
    if (exists) {
      return ContentService.createTextOutput(JSON.stringify({status: "error", message: "Användaren finns redan"})).setMimeType(ContentService.MimeType.JSON);
    }
    
    usersSheet.appendRow([
      data.name,
      String(data.pin),
      data.group,
      JSON.stringify({}),
      new Date().toISOString(),
      0,
      0
    ]);
    return ContentService.createTextOutput(JSON.stringify({status: "success", action: "create_user"})).setMimeType(ContentService.MimeType.JSON);
  }
  
  // 4. SPARA EN ELEVS PROGRESSION
  if (action === "save_progress") {
    var rows = usersSheet.getDataRange().getValues();
    var rowIndex = -1;
    for (var i = 1; i < rows.length; i++) {
      var row = rows[i];
      if (row && row[col_name] && row[col_name].toString().toLowerCase() === data.name.toString().toLowerCase()) {
        rowIndex = i + 1; // Hitta exakt rad i Google Sheets (1-baserad)
        break;
      }
    }
    
    if (rowIndex === -1) {
      return ContentService.createTextOutput(JSON.stringify({status: "error", message: "Hittade inte eleven"})).setMimeType(ContentService.MimeType.JSON);
    }
    
    usersSheet.getRange(rowIndex, col_leitner + 1).setValue(JSON.stringify(data.leitner)); // Kolumn D
    usersSheet.getRange(rowIndex, col_saved + 1).setValue(new Date().toISOString());     // Kolumn E
    usersSheet.getRange(rowIndex, col_score + 1).setValue(data.score || 0);               // Kolumn F
    usersSheet.getRange(rowIndex, col_total + 1).setValue(data.total || 0);               // Kolumn G
    
    return ContentService.createTextOutput(JSON.stringify({status: "success", action: "save_progress"})).setMimeType(ContentService.MimeType.JSON);
  }
  
  return ContentService.createTextOutput(JSON.stringify({status: "error", message: "Okänd åtgärd"})).setMimeType(ContentService.MimeType.JSON);
}
