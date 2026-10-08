from concurrent.futures import ThreadPoolExecutor
import json
import pytest
from core.leitner import initial
from services.database import Conflict, LocalDatabase, ServiceError


@pytest.fixture
def db(tmp_path):
    return LocalDatabase(tmp_path/'test.sqlite3', 'teacher-password-test')


def account(db, name='Test', group='2A', pin='0123'):
    teacher = db.teacher_login('teacher-password-test')['token']
    db.create_user(teacher,name,group,pin)
    return db.authenticate(name,group,pin)['token'], teacher


def test_pin_is_hashed_and_scope_is_enforced(db):
    token,teacher = account(db)
    with db.connection() as conn:
        row = conn.execute('SELECT * FROM users').fetchone()
        assert row['pin_hash'] != '0123' and '0123' not in json.dumps(db.students(teacher))
    with pytest.raises(ServiceError):
        db.students(token)
    with pytest.raises(ServiceError):
        db.create_user(token,'other','2A','1234')
    db.logout(token)
    with pytest.raises(ServiceError):
        db.load_progress(token)


def test_persistence_idempotency_and_stale_write_protection(db):
    token,_ = account(db)
    assert db.save_progress(token, {'word':initial()},0,'operation-a') == 1
    assert db.save_progress(token, {'word':initial()},0,'operation-a') == 1
    with pytest.raises(Conflict):
        db.save_progress(token, {},0,'operation-old')
    other = LocalDatabase(db.path)
    assert other.load_progress(token)['progress'] == {'word':initial()}
    assert db.save_progress(token,{},1,'operation-b') == 2
    with pytest.raises(Conflict):
        db.save_progress(token, {'word':initial()},0,'operation-a')


def test_two_simultaneous_sessions_cannot_overwrite_each_other(db):
    token,_ = account(db)
    def save(operation):
        try:
            db.save_progress(token,{operation:initial()},0,operation)
            return 'saved'
        except Conflict:
            return 'conflict'
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(save,['one','two'])) == ['conflict','saved']


def test_login_is_rate_limited_across_connections(db):
    account(db)
    for _ in range(5):
        with pytest.raises(ServiceError, match='Felaktiga'):
            db.authenticate('Test','2A','9999')
    with pytest.raises(ServiceError, match='15 minuter'):
        LocalDatabase(db.path).authenticate('Test','2A','0123')


def test_no_default_admin_password(db,tmp_path):
    with pytest.raises(ServiceError,match='inte konfigurerat'):
        LocalDatabase(tmp_path/'missing.sqlite3').teacher_login('skola123')


def test_teacher_lists_and_import_preserve_revision_guard(db):
    from data.vocabulary import builtin_lists
    token,teacher = account(db)
    db.save_lists(teacher,builtin_lists())
    assert len(db.get_lists()) == 8
    student = db.students(teacher)[0]
    db.import_progress(teacher,student['id'],{'word':initial()},0)
    assert db.load_progress(token)['revision'] == 1
    with pytest.raises(Conflict):
        db.import_progress(teacher,student['id'],{},0)


def test_name_and_pin_choose_the_correct_account_and_keep_progress(db):
    _, teacher = account(db, name='Alex', group='2A', pin='0123')
    db.create_user(teacher, 'Alex', '2B', '0456')
    first = db.authenticate_student(' Alex ', '0123')
    second = db.authenticate_student('Alex', '0456')
    assert first['group'] == '2A' and second['group'] == '2B'
    assert first['id'] != second['id']
    db.save_progress(first['token'], {'word': initial()}, 0, 'first')
    assert db.load_progress(db.authenticate_student('Alex', '0123')['token'])['progress'] == {'word': initial()}
    assert db.load_progress(second['token'])['progress'] == {}
    with pytest.raises(ServiceError, match='Samma namn och PIN'):
        db.create_user(teacher, 'Alex', '2C', '0123')


def test_old_duplicate_name_and_pin_cannot_issue_a_session(db):
    account(db, name='Alex', group='2A', pin='0123')
    # Represent two existing accounts from before name-only login was introduced.
    with db.connection() as conn:
        row = conn.execute('SELECT * FROM users').fetchone()
        conn.execute('INSERT INTO users(id,name,class_name,salt,pin_hash) VALUES(?,?,?,?,?)',
                     ('legacy-duplicate', 'Alex', '2B', row['salt'], row['pin_hash']))
        before = conn.execute('SELECT count(*) FROM sessions').fetchone()[0]
    with pytest.raises(ServiceError, match='Felaktiga'):
        db.authenticate_student('Alex', '0123')
    with db.connection() as conn:
        assert conn.execute('SELECT count(*) FROM sessions').fetchone()[0] == before


def test_name_only_login_lockout_is_shared_with_legacy_login(db):
    account(db)
    for _ in range(5):
        with pytest.raises(ServiceError, match='Felaktiga'):
            db.authenticate_student('Test', '9999')
    with pytest.raises(ServiceError, match='15 minuter'):
        LocalDatabase(db.path).authenticate_student('Test', '0123')
    with pytest.raises(ServiceError, match='15 minuter'):
        db.authenticate('Test', '2A', '0123')


def test_sheets_client_sends_only_name_and_pin_and_explains_old_backend(monkeypatch):
    from services.database import SessionExpired
    from services.gsheets import SheetsDatabase
    db = SheetsDatabase('https://script.google.com/macros/s/test/exec', 'k' * 32)
    calls = []
    def request(action, **values):
        calls.append((action, values))
        return {'token':'test-token', 'id':'student-id', 'group':'2A'}
    monkeypatch.setattr(db, 'request', request)
    assert db.authenticate_student(' Alex ', '0123')['id'] == 'student-id'
    assert calls == [('authenticate_student', {'name':'Alex', 'pin':'0123'})]
    def old_backend(*args, **kwargs):
        raise SessionExpired('Logga in igen')
    monkeypatch.setattr(db, 'request', old_backend)
    with pytest.raises(ServiceError, match='Google Apps Script-versionen'):
        db.authenticate_student('Alex', '0123')
