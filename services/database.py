"""Lokal databas för utveckling/egen server med beständig disk."""
import hashlib
import hmac
import json
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


class ServiceError(Exception):
    pass


class Conflict(ServiceError):
    pass


class SessionExpired(ServiceError):
    pass


def validate_progress(progress):
    if not isinstance(progress, dict) or len(progress) > 60000:
        raise ServiceError("Ogiltig progression.")
    for key, state in progress.items():
        if not isinstance(key, str) or len(key) > 400 or not isinstance(state, dict):
            raise ServiceError("Ogiltig progression.")
        if state.get("box") not in (1, 2, 3):
            raise ServiceError("Ogiltig låda.")
        for field in ("attempts", "correct", "next_review"):
            value = state.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 10**12:
                raise ServiceError("Ogiltig progression.")
        if state["correct"] > state["attempts"]:
            raise ServiceError("Ogiltig progression.")
    return progress


def pin_hash(pin, salt):
    return hashlib.scrypt(pin.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


class LocalDatabase:
    def __init__(self, path, admin_password=""):
        self.path = str(path)
        self.admin_password = admin_password
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY, name TEXT, class_name TEXT, salt TEXT, pin_hash TEXT,
                    progress TEXT DEFAULT '{}', revision INTEGER DEFAULT 0, last_operation TEXT,
                    UNIQUE(name, class_name));
                CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id TEXT, role TEXT, expires REAL);
                CREATE TABLE IF NOT EXISTS failures (identity TEXT PRIMARY KEY, count INTEGER, started REAL);
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
            ''')

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        except sqlite3.IntegrityError:
            raise
        except sqlite3.Error:
            raise ServiceError("Databasen kunde inte slutföra åtgärden. Kontrollera att lagringen är tillgänglig och försök igen.") from None
        finally:
            db.close()

    def _login(self, identity, check, user_id, role, name):
        now = time.time()
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM sessions WHERE expires < ?", (now,))
            failure = db.execute("SELECT * FROM failures WHERE identity=?", (identity,)).fetchone()
            count = failure["count"] if failure and now - failure["started"] < 900 else 0
            if count >= 5:
                raise ServiceError("För många försök. Vänta 15 minuter.")
            if not check():
                started = failure["started"] if count else now
                db.execute("INSERT OR REPLACE INTO failures VALUES(?,?,?)", (identity, count + 1, started))
                # Commit lockout before reporting failed login.
                db.commit()
                raise ServiceError("Felaktiga inloggningsuppgifter.")
            db.execute("DELETE FROM failures WHERE identity=?", (identity,))
            token = secrets.token_urlsafe(32)
            db.execute("INSERT INTO sessions VALUES(?,?,?,?)", (token_hash(token), user_id, role, now + 28800))
        return {"token": token, "name": name, "role": role}

    def authenticate(self, name, group, pin):
        name, group = name.strip(), group.strip()
        with self.connection() as db:
            user = db.execute("SELECT * FROM users WHERE name=? AND class_name=?", (name, group)).fetchone()
        salt = user["salt"] if user else "00" * 16
        result = self._login("student:" + name + "\0" + group,
            lambda: hmac.compare_digest(pin_hash(pin, salt), user["pin_hash"] if user else "0" * 128),
            user["id"] if user else "", "student", name)
        return {**result, "group": group, "id": user["id"]}

    def teacher_login(self, password):
        if not self.admin_password:
            raise ServiceError("Lärarlösenord är inte konfigurerat.")
        return self._login("teacher", lambda: hmac.compare_digest(password.encode(), self.admin_password.encode()), "teacher", "teacher", "Lärare")

    def _session(self, db, token, teacher=False):
        row = db.execute("SELECT * FROM sessions WHERE token=? AND expires>?", (token_hash(token), time.time())).fetchone()
        if not row:
            raise SessionExpired("Logga in igen för att fortsätta.")
        if teacher and row["role"] != "teacher":
            raise ServiceError("Lärarbehörighet krävs.")
        return row

    def logout(self, token):
        with self.connection() as db:
            db.execute("DELETE FROM sessions WHERE token=?", (token_hash(token),))

    def create_user(self, token, name, group, pin):
        if not name.strip() or not group.strip() or len(name) > 100 or len(group) > 100 or not pin.isascii() or not pin.isdigit() or len(pin) != 4:
            raise ServiceError("Ange namn, klass och exakt fyra siffror i PIN-koden.")
        salt = secrets.token_hex(16)
        digest = pin_hash(pin, salt)
        try:
            with self.connection() as db:
                self._session(db, token, teacher=True)
                db.execute("INSERT INTO users(id,name,class_name,salt,pin_hash) VALUES(?,?,?,?,?)", (uuid4().hex, name.strip(), group.strip(), salt, digest))
        except sqlite3.IntegrityError:
            raise ServiceError("Det namnet finns redan i klassen.") from None

    def load_progress(self, token):
        with self.connection() as db:
            session = self._session(db, token)
            user = db.execute("SELECT progress,revision FROM users WHERE id=?", (session["user_id"],)).fetchone()
            if not user:
                raise ServiceError("Kontot saknas.")
            return {"progress": json.loads(user["progress"]), "revision": user["revision"]}

    def save_progress(self, token, progress, expected_revision, operation_id):
        validate_progress(progress)
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            session = self._session(db, token)
            row = db.execute("SELECT revision,last_operation FROM users WHERE id=?", (session["user_id"],)).fetchone()
            if not row:
                raise ServiceError("Kontot saknas.")
            if row["last_operation"] == operation_id:
                return row["revision"]
            if row["revision"] != expected_revision:
                raise Conflict("Framstegen ändrades i en annan flik. Hämta den sparade versionen.")
            revision = expected_revision + 1
            db.execute("UPDATE users SET progress=?,revision=?,last_operation=? WHERE id=?", (json.dumps(progress), revision, operation_id, session["user_id"]))
            return revision

    def get_lists(self):
        with self.connection() as db:
            row = db.execute("SELECT value FROM settings WHERE key='lists'").fetchone()
            return json.loads(row["value"]) if row else []

    def save_lists(self, token, lists):
        from data.vocabulary import validate_lists
        validate_lists(lists)
        with self.connection() as db:
            self._session(db, token, teacher=True)
            db.execute("INSERT OR REPLACE INTO settings VALUES('lists',?)", (json.dumps(lists, ensure_ascii=False),))

    def students(self, token):
        with self.connection() as db:
            self._session(db, token, teacher=True)
            return [{"id": row["id"], "name": row["name"], "group": row["class_name"], "progress": json.loads(row["progress"]), "revision": row["revision"]} for row in db.execute("SELECT id,name,class_name,progress,revision FROM users ORDER BY class_name,name")]

    def import_progress(self, token, student_id, progress, expected_revision):
        validate_progress(progress)
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            self._session(db, token, teacher=True)
            row = db.execute("SELECT revision FROM users WHERE id=?", (student_id,)).fetchone()
            if not row or row["revision"] != expected_revision:
                raise Conflict("Elevens framsteg ändrades. Öppna lärarpanelen igen och försök på nytt.")
            db.execute("UPDATE users SET progress=?,revision=revision+1,last_operation=NULL WHERE id=?", (json.dumps(progress), student_id))
