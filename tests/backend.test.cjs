const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

// Contract tests using a Sheets/Apps Script API double. Not a live Google test.
function backend() {
  class Sheet {
    constructor() { this.data = []; this.cols = 26; }
    getMaxColumns() { return this.cols; }
    insertColumnsAfter(after, n) { this.cols += n; }
    getLastRow() { return this.data.length; }
    getLastColumn() { return Math.max(0, ...this.data.map(r => r.length)); }
    getRange(r,c,h,w) {
      assert(c+w-1 <= this.cols, 'columns must exist');
      const self = this;
      return {
        getValues() { return Array.from({length:h}, (_,i) => Array.from({length:w},(_,j) => self.data[r-1+i]?.[c-1+j] ?? '')); },
        setValues(values) {
          assert.equal(values.length,h);
          values.forEach((row,i) => { assert.equal(row.length,w); self.data[r-1+i] ??= []; row.forEach((v,j) => {
            assert(!(typeof v === 'string' && v.startsWith('=')), 'formula injection');
            self.data[r-1+i][c-1+j] = v;
          }); });
          return this;
        },
        setNumberFormat() { return this; }
      };
    }
    appendRow(row) { this.data.push([...row]); }
    deleteRow(row) { this.data.splice(row-1,1); }
    deleteRows(row,n) { this.data.splice(row-1,n); }
  }
  const props = {API_KEY:'a'.repeat(48),PIN_PEPPER:'p'.repeat(48),ADMIN_PASSWORD:'a-good-teacher-password',SPREADSHEET_ID:'test-sheet'};
  const sheets = {};
  let held = false;
  const context = vm.createContext({
    PropertiesService:{getScriptProperties:() => ({getProperty:k => props[k]})},
    SpreadsheetApp:{openById:() => ({getSheetByName:n => sheets[n],insertSheet:n => (sheets[n] = new Sheet())}),flush() {}},
    Utilities:{
      getUuid:() => crypto.randomUUID(),DigestAlgorithm:{SHA_256:'sha256'},Charset:{UTF_8:'utf8'},
      computeDigest:(alg,value) => crypto.createHash('sha256').update(value).digest(),
      computeHmacSha256Signature:(v,key) => crypto.createHmac('sha256',key).update(v).digest(),
      base64EncodeWebSafe:b => Buffer.from(b).toString('base64url')
    },
    ContentService:{MimeType:{JSON:'json'},createTextOutput:t => ({setMimeType:() => t})},
    LockService:{getScriptLock:() => ({tryLock:() => {assert(!held); held=true; return true;},releaseLock:() => {held=false;}})}
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../backend/Code.gs'),'utf8'),context);
  const call = (action,values={}) => {
    const result = JSON.parse(context.doPost({postData:{contents:JSON.stringify({api_key:props.API_KEY,action,...values})}}));
    assert.equal(held,false);
    return result;
  };
  return {call,sheets,props};
}

function account(b) {
  const teacher = b.call('teacher_login',{password:b.props.ADMIN_PASSWORD}).data.token;
  assert.equal(b.call('create_user',{token:teacher,name:'Test',group:'2A',pin:'0123'}).ok,true);
  const login = b.call('authenticate',{name:'Test',group:'2A',pin:'0123'});
  assert.equal(login.ok,true);
  return {teacher,student:login.data.token};
}

test('API key, role checks and secret-free student authentication',() => {
  const b = backend();
  assert.equal(b.call('get_lists',{api_key:'wrong'}).ok,false);
  const {teacher,student} = account(b);
  assert.equal(b.call('students',{token:student}).ok,false);
  assert.equal(b.call('create_user',{token:student,name:'Other',group:'2A',pin:'1234'}).ok,false);
  const summary = b.call('students',{token:teacher});
  assert.equal(summary.ok,true);
  assert(!JSON.stringify(summary).includes('0123'));
  assert(!JSON.stringify(summary).includes('digest'));
  assert.notEqual(b.sheets.Users_v2.data[1][4],'0123');
  assert.equal(b.call('logout',{token:student}).ok,true);
  assert.equal(b.call('load_progress',{token:student}).ok,false);
});

test('Revision conflict and retry after an uncertain save',() => {
  const b = backend();
  const {student} = account(b);
  const state = {box:2,attempts:1,correct:1,last_reviewed:100,next_review:259300};
  const request = {token:student,progress:{word:state},expected_revision:0,operation_id:'op-a'};
  assert.equal(b.call('save_progress',request).data,1);
  assert.equal(b.call('save_progress',request).data,1);
  assert.equal(b.call('save_progress',{...request,operation_id:'old'}).code,'conflict');
  assert.deepEqual(b.call('load_progress',{token:student}).data,{progress:{word:state},revision:1});
  assert.equal(b.call('save_progress',{...request,progress:{},expected_revision:1,operation_id:'op-b'}).data,2);
  assert.equal(b.call('save_progress',request).code,'conflict');
});

test('Login lockout persists across requests and accepts a leading zero PIN',() => {
  const b = backend(); account(b);
  for(let i=0;i<5;i++) assert.equal(b.call('authenticate',{name:'Test',group:'2A',pin:'9999'}).ok,false);
  assert.match(b.call('authenticate',{name:'Test',group:'2A',pin:'0123'}).message,/15 minuter/);
});

test('Lists round trip, chunked progress and formula protection',() => {
  const b = backend();
  const {teacher,student} = account(b);
  const lists = JSON.parse(fs.readFileSync(path.join(__dirname,'../data/vocabulary.json'),'utf8'));
  assert.equal(b.call('save_lists',{token:teacher,lists}).ok,true);
  assert.deepEqual(b.call('get_lists').data,lists);
  const progress = {};
  for(let i=0;i<600;i++) progress['word_'+i] = {box:1,attempts:1,correct:0,last_reviewed:100,next_review:700};
  assert.equal(b.call('save_progress',{token:student,progress,expected_revision:0,operation_id:'large'}).ok,true);
  assert.deepEqual(b.call('load_progress',{token:student}).data.progress,progress);
  assert.equal(b.call('create_user',{token:teacher,name:'=IMPORTXML("evil")',group:'2A',pin:'1234'}).ok,false);
});

test('Teacher import is protected by role and revision',() => {
  const b = backend(); const {teacher,student} = account(b);
  const id = b.call('students',{token:teacher}).data[0].id;
  const request = {student_id:id,progress:{},expected_revision:0};
  assert.equal(b.call('import_progress',{...request,token:student}).ok,false);
  assert.equal(b.call('import_progress',{...request,token:teacher}).data,1);
  assert.equal(b.call('import_progress',{...request,token:teacher}).code,'conflict');
});

test('Name/PIN login selects exactly one existing account and preserves progress',() => {
  const b = backend(); const {teacher,student} = account(b);
  assert.equal(b.call('create_user',{token:teacher,name:'Test',group:'2B',pin:'0456'}).ok,true);
  assert.equal(b.call('create_user',{token:teacher,name:'Test',group:'2C',pin:'0123'}).ok,false);
  const first=b.call('authenticate_student',{name:' Test ',pin:'0123'});
  const second=b.call('authenticate_student',{name:'Test',pin:'0456'});
  assert.equal(first.data.group,'2A'); assert.equal(second.data.group,'2B');
  assert.notEqual(first.data.id,second.data.id);
  const state={box:2,attempts:1,correct:1,last_reviewed:100,next_review:259300};
  assert.equal(b.call('save_progress',{token:student,progress:{word:state},expected_revision:0,operation_id:'saved'}).ok,true);
  assert.deepEqual(b.call('load_progress',{token:first.data.token}).data.progress,{word:state});
  assert.deepEqual(b.call('load_progress',{token:second.data.token}).data.progress,{});
  // Simulate a duplicate from the old backend without changing either user's ID.
  b.sheets.Users_v2.data[2][3]=b.sheets.Users_v2.data[1][3];
  b.sheets.Users_v2.data[2][4]=b.sheets.Users_v2.data[1][4];
  const sessions=b.sheets.Sessions_v2.getLastRow();
  assert.equal(b.call('authenticate_student',{name:'Test',pin:'0123'}).ok,false);
  assert.equal(b.sheets.Sessions_v2.getLastRow(),sessions);
});

test('Name/PIN login lockout is shared with legacy login',() => {
  const b = backend(); account(b);
  for(let i=0;i<5;i++) assert.equal(b.call('authenticate_student',{name:'Test',pin:'9999'}).ok,false);
  assert.match(b.call('authenticate_student',{name:'Test',pin:'0123'}).message,/15 minuter/);
  assert.match(b.call('authenticate',{name:'Test',group:'2A',pin:'0123'}).message,/15 minuter/);
});
