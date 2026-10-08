/** GlosFlow v2. A new, separate spreadsheet is required. See README.md. */
const USER_HEADERS = ['id', 'name', 'group', 'salt', 'digest', 'revision', 'operation', ...Array.from({length: 20}, (_, i) => 'progress_' + i)];
const SESSION_HEADERS = ['digest', 'user_id', 'role', 'expires'];
const FAILURE_HEADERS = ['identity', 'count', 'started'];
const LIST_HEADERS = ['id', ...Array.from({length: 10}, (_, i) => 'json_' + i)];
const AUDIO_HEADERS = ['key', 'text', 'language', 'voice', ...Array.from({length: 5}, (_, i) => 'mp3_' + i)];

function properties() { return PropertiesService.getScriptProperties(); }
function fail(message, code) { const e = new Error(message); e.code = code || 'error'; throw e; }
function jsonOutput(value) { return ContentService.createTextOutput(JSON.stringify(value)).setMimeType(ContentService.MimeType.JSON); }
function sheet(name, headers) {
  const id = properties().getProperty('SPREADSHEET_ID');
  if (!id) fail('Databasen är inte konfigurerad.');
  const book = SpreadsheetApp.openById(id);
  let s = book.getSheetByName(name);
  if (!s) {
    s = book.insertSheet(name);
    if (s.getMaxColumns() < headers.length) s.insertColumnsAfter(s.getMaxColumns(), headers.length-s.getMaxColumns());
    s.getRange(1, 1, 1, headers.length).setValues([headers]);
  }
  const current = s.getRange(1, 1, 1, headers.length).getValues()[0];
  if (JSON.stringify(current) !== JSON.stringify(headers)) fail('Felaktigt tabellformat. Använd ett nytt kalkylblad för v2.');
  return s;
}
function rows(s) { return s.getLastRow() > 1 ? s.getRange(2, 1, s.getLastRow()-1, s.getLastColumn()).getValues() : []; }
function hash(value) { return Utilities.base64EncodeWebSafe(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, String(value), Utilities.Charset.UTF_8)); }
function equal(a, b) {
  a = String(a); b = String(b);
  let diff = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i++) diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return diff === 0;
}
function pinDigest(pin, salt) {
  const pepper = properties().getProperty('PIN_PEPPER');
  if (!pepper || pepper.length < 32) fail('PIN-skyddet är inte konfigurerat.');
  return Utilities.base64EncodeWebSafe(Utilities.computeHmacSha256Signature(salt + ':' + pin, pepper, Utilities.Charset.UTF_8));
}
function chunks(value, count) {
  const text = JSON.stringify(value);
  if (text.length > 40000 * count) fail('Datan är för stor för denna databas.');
  // Delar hålls långt under Sheets gräns för en cell. Parse sker efter sammanfogning.
  return Array.from({length: count}, (_, i) => text.slice(i*40000, (i+1)*40000));
}
function progressOf(row) { return JSON.parse(row.slice(7, 27).join('') || '{}'); }
function validProgress(progress) {
  if (!progress || typeof progress !== 'object' || Array.isArray(progress) || Object.keys(progress).length > 60000) fail('Ogiltig progression.');
  Object.entries(progress).forEach(([k, s]) => {
    if (k.length > 400 || !s || ![1,2,3].includes(s.box)) fail('Ogiltig progression.');
    ['attempts','correct','next_review'].forEach(f => { if (typeof s[f] !== 'number' || !Number.isFinite(s[f]) || s[f] < 0 || s[f] > 1e12) fail('Ogiltig progression.'); });
    if (s.correct > s.attempts) fail('Ogiltig progression.');
  });
  chunks(progress, 20);
  return progress;
}
function validLists(lists) {
  if (!Array.isArray(lists) || lists.length < 1 || lists.length > 100) fail('Ogiltigt glosbibliotek.');
  const ids = new Set();
  lists.forEach(v => {
    ['id','name','language','category'].forEach(f => { if (typeof v[f] !== 'string' || !v[f].trim() || v[f].length > 160) fail('Ogiltig gloslista.'); });
    if (!/^[a-zA-Z0-9_-]+$/.test(v.id)) fail('Ogiltigt list-ID.');
    if (ids.has(v.id)) fail('Dubblerat list-ID.'); ids.add(v.id);
    if (!Array.isArray(v.words) || v.words.length < 1 || v.words.length > 300) fail('Ogiltig gloslista.');
    const words = new Set();
    v.words.forEach(w => {
      if (typeof w.id !== 'string' || !/^[a-zA-Z0-9_-]{1,160}$/.test(w.id) || words.has(w.id) || typeof w.svenska !== 'string' || !w.svenska || w.svenska.length > 300) fail('Ogiltigt ord.');
      words.add(w.id);
      ['accepted_answers','swedish_answers'].forEach(f => {
        if (!Array.isArray(w[f]) || w[f].length < 1 || w[f].length > 20 || w[f].some(x => typeof x !== 'string' || !x.trim() || x.length > 300)) fail('Ogiltiga svar.');
      });
      if (w.memory_tip !== undefined && (typeof w.memory_tip !== 'string' || w.memory_tip.length > 2000)) fail('Ogiltigt minnestips.');
    });
    chunks(v, 10);
  });
  return lists;
}
// Ljud från Azure Speech som läraren har skapat. Ett ljud per rad, mp3 som base64 i upp till fem celler.
function validClip(key, c) {
  if (!/^[0-9a-f]{64}$/.test(key) || !c || typeof c !== 'object') fail('Ogiltigt ljud.');
  if (typeof c.text !== 'string' || !c.text.trim() || c.text.length > 300 || c.text.startsWith('=')) fail('Ogiltigt ljud.');
  if (typeof c.language !== 'string' || !/^[a-z]{2}-[A-Z]{2}$/.test(c.language)) fail('Ogiltigt ljud.');
  if (typeof c.voice !== 'string' || !/^[a-z]{2}-[A-Z]{2}-[A-Za-z]+Neural$/.test(c.voice)) fail('Ogiltigt ljud.');
  if (typeof c.mp3 !== 'string' || c.mp3.length > 200000 || !/^[A-Za-z0-9+/]+=*$/.test(c.mp3)) fail('Ogiltigt ljud.');
  return [key, c.text, c.language, c.voice, ...Array.from({length: 5}, (_, i) => c.mp3.slice(i*40000, (i+1)*40000))];
}
function audioClips() {
  const clips = {};
  rows(sheet('Audio_v2', AUDIO_HEADERS)).forEach(r => {
    clips[r[0]] = {text: String(r[1]), language: String(r[2]), voice: String(r[3]), mp3: r.slice(4, 9).join('')};
  });
  return clips;
}
function saveAudio(clips) {
  if (!clips || typeof clips !== 'object' || Array.isArray(clips) || Object.keys(clips).length > 60) fail('Ogiltigt ljud.');
  const s = sheet('Audio_v2', AUDIO_HEADERS);
  const existing = rows(s).map(r => r[0]);
  Object.entries(clips).forEach(([key, clip]) => {
    const row = validClip(key, clip);
    const i = existing.indexOf(key);
    const at = i >= 0 ? i+2 : s.getLastRow()+1;
    // Texten lagras som text, aldrig som kalkylbladsformel.
    s.getRange(at, 1, 1, AUDIO_HEADERS.length).setNumberFormat('@').setValues([row]);
    if (i < 0) existing.push(key);
  });
  return Object.keys(clips).length;
}
function login(identity, valid, userId, role, name) {
  const f = sheet('Failures_v2', FAILURE_HEADERS);
  const data = rows(f);
  const now = Date.now();
  let i = data.findIndex(r => r[0] === hash(identity));
  const old = i >= 0 ? data[i] : [hash(identity), 0, now];
  const count = now - Number(old[2]) < 900000 ? Number(old[1]) : 0;
  if (count >= 5) fail('För många försök. Vänta 15 minuter.');
  if (!valid) {
    const row = [hash(identity), count+1, count ? old[2] : now];
    if (i >= 0) f.getRange(i+2,1,1,3).setValues([row]); else f.appendRow(row);
    fail('Felaktiga inloggningsuppgifter.');
  }
  if (i >= 0) f.deleteRow(i+2);
  const s = sheet('Sessions_v2', SESSION_HEADERS);
  const expired = rows(s);
  for (let j = expired.length-1; j >= 0; j--) if (Number(expired[j][3]) < now) s.deleteRow(j+2);
  const token = Utilities.getUuid() + Utilities.getUuid();
  s.appendRow([hash(token), userId, role, now+28800000]);
  return {token, name, role};
}
function session(token, teacher) {
  if (typeof token !== 'string') fail('Logga in igen för att fortsätta.', 'auth');
  const s = sheet('Sessions_v2', SESSION_HEADERS);
  const row = rows(s).find(r => r[0] === hash(token) && Number(r[3]) > Date.now());
  if (!row) fail('Logga in igen för att fortsätta.', 'auth');
  if (teacher && row[2] !== 'teacher') fail('Lärarbehörighet krävs.');
  return {user_id: row[1], role: row[2]};
}
function writeProgress(users, index, row, progress, expected, operation) {
  if (operation && row[6] === operation) return Number(row[5]);
  if (!Number.isInteger(expected) || Number(row[5]) !== expected) fail('Framstegen ändrades i en annan flik.', 'conflict');
  const parts = chunks(validProgress(progress), 20);
  const revision = expected+1;
  // Revision, operations-ID och hela snapshoten skrivs i EN setValues under lås.
  users.getRange(index+2,6,1,22).setValues([[revision, operation || '', ...parts]]);
  return revision;
}
function dispatch(p) {
  const action = p.action;
  if (action === 'get_lists') return rows(sheet('Lists_v2', LIST_HEADERS)).map(r => JSON.parse(r.slice(1).join('')));
  if (action === 'get_audio') return audioClips();
  if (action === 'teacher_login') {
    const configured = properties().getProperty('ADMIN_PASSWORD');
    if (!configured || configured.length < 12) fail('Lärarlösenord är inte konfigurerat (minst 12 tecken).');
    return login('teacher', equal(hash(p.password || ''), hash(configured)), 'teacher', 'teacher', 'Lärare');
  }
  const users = sheet('Users_v2', USER_HEADERS);
  const data = rows(users);
  if (action === 'authenticate' || action === 'authenticate_student') {
    const name = String(p.name || '').trim(), group = String(p.group || '').trim();
    const pin = String(p.pin || '');
    if (!name || name.length > 100 || group.length > 100 || !/^\d{4}$/.test(pin)) fail('Ange namn och exakt fyra siffror i PIN-koden.');
    const candidates = data.filter(r => r[1] === name && (action === 'authenticate_student' || r[2] === group));
    const matches = candidates.filter(r => equal(pinDigest(pin, r[3]), r[4]));
    if (!candidates.length) pinDigest(pin, 'unknown');
    const row = matches.length === 1 ? matches[0] : null;
    const result = login('student:' + name, !!row, row ? row[0] : '', 'student', name);
    return {...result, group:row[2], id:row[0]};
  }
  if (action === 'logout') {
    session(p.token, false);
    const s = sheet('Sessions_v2', SESSION_HEADERS), i = rows(s).findIndex(r => r[0] === hash(p.token));
    if (i >= 0) s.deleteRow(i+2);
    return null;
  }
  if (['load_progress','save_progress'].includes(action)) {
    const user = session(p.token, false);
    if (user.role !== 'student') fail('Elevkonto krävs.');
    const i = data.findIndex(r => r[0] === user.user_id), row = data[i];
    if (!row) fail('Kontot saknas.');
    if (action === 'load_progress') return {progress: progressOf(row), revision: Number(row[5])};
    if (typeof p.operation_id !== 'string' || !p.operation_id || p.operation_id.length > 100) fail('Operations-ID saknas.');
    return writeProgress(users, i, row, p.progress, p.expected_revision, p.operation_id);
  }
  session(p.token, true);
  if (action === 'create_user') {
    const name = String(p.name || '').trim(), group = String(p.group || '').trim(), pin = String(p.pin || '');
    if (!name || !group || name.startsWith('=') || group.startsWith('=') || name.length > 100 || group.length > 100 || !/^\d{4}$/.test(pin)) fail('Ange namn, klass och fyra siffror i PIN-koden. Namn och klass får inte börja med =.');
    if (data.some(r => r[1] === name && r[2] === group)) fail('Det namnet finns redan i klassen.');
    if (data.some(r => r[1] === name && equal(pinDigest(pin, r[3]), r[4]))) fail('Samma namn och PIN-kod används redan. Välj en annan PIN-kod eller ett tydligare elevnamn.');
    const salt = Utilities.getUuid();
    const row = [Utilities.getUuid(), name, group, salt, pinDigest(pin, salt), 0, '', ...chunks({}, 20)];
    // Namn/klass från användare lagras som text, aldrig som kalkylbladsformler.
    users.getRange(users.getLastRow()+1,1,1,27).setNumberFormat('@').setValues([row]);
    return null;
  }
  if (action === 'students') return data.map(r => ({id:r[0], name:r[1], group:r[2], progress:progressOf(r), revision:Number(r[5])}));
  if (action === 'import_progress') {
    const i = data.findIndex(r => r[0] === p.student_id);
    if (i < 0) fail('Kontot saknas.');
    return writeProgress(users, i, data[i], p.progress, p.expected_revision, '');
  }
  if (action === 'save_audio') return saveAudio(p.clips);
  if (action === 'save_lists') {
    const values = validLists(p.lists).map(v => [v.id, ...chunks(v,10)]);
    const s = sheet('Lists_v2', LIST_HEADERS);
    s.getRange(2,1,values.length,11).setValues(values);
    const excess = s.getLastRow()-1-values.length;
    if (excess > 0) s.deleteRows(values.length+2, excess);
    return null;
  }
  fail('Okänd åtgärd.');
}
function doPost(e) {
  const lock = LockService.getScriptLock();
  let held = false;
  try {
    const raw = e && e.postData && e.postData.contents;
    if (!raw || raw.length > 1200000) fail('Ogiltig begäran.');
    const p = JSON.parse(raw);
    const key = properties().getProperty('API_KEY');
    if (!key || key.length < 32 || typeof p.api_key !== 'string' || !equal(hash(p.api_key), hash(key))) fail('Åtkomst nekad.');
    if (!lock.tryLock(10000)) fail('Databasen är upptagen. Försök igen.');
    held = true;
    return jsonOutput({ok:true, data:dispatch(p)});
  } catch (error) {
    return jsonOutput({ok:false, code:error.code || 'error', message:error.code || error.message === 'Felaktiga inloggningsuppgifter.' ? error.message : 'Databasen kunde inte slutföra åtgärden. Kontrollera konfigurationen eller försök igen.'});
  } finally {
    if (held) { SpreadsheetApp.flush(); lock.releaseLock(); }
  }
}
function doGet() { return jsonOutput({ok:false, message:'GlosFlow använder autentiserade POST-anrop.'}); }
