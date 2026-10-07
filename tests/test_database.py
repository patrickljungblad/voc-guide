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
