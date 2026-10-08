"""Server-till-server-klient till backend/Code.gs. Ingen elevlista med PIN skickas."""
import json
import urllib.request
from urllib.parse import urlparse
from services.database import Conflict, ServiceError, SessionExpired


class SheetsDatabase:
    def __init__(self, url, api_key):
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != "script.google.com" or not parsed.path.endswith("/exec") or len(api_key) < 32:
            raise ServiceError("Konfigurera en Google Apps Script /exec-adress och en API-nyckel på minst 32 tecken.")
        self.url, self.api_key = url, api_key

    def request(self, action, **values):
        payload = {"action": action, "api_key": self.api_key, **values}
        req = urllib.request.Request(self.url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                result = json.loads(response.read())
        except Exception:
            raise ServiceError("Databasen kunde inte nås. Ditt svar finns kvar här; försök spara igen.") from None
        if not result.get("ok"):
            if result.get("code") == "auth":
                raise SessionExpired("Logga in igen för att fortsätta.")
            if result.get("code") == "conflict":
                raise Conflict("Framstegen ändrades i en annan flik. Hämta den sparade versionen.")
            raise ServiceError(result.get("message", "Databasen kunde inte slutföra åtgärden."))
        return result.get("data")

    def authenticate(self, name, group, pin):
        return self.request("authenticate", name=name.strip(), group=group.strip(), pin=pin)

    def authenticate_student(self, name, pin):
        try:
            return self.request("authenticate_student", name=name.strip(), pin=pin)
        except SessionExpired:
            raise ServiceError("Elevinloggningen behöver den nya Google Apps Script-versionen. Be läraren följa UPPDATERING.md.") from None

    def teacher_login(self, password):
        return self.request("teacher_login", password=password)

    def logout(self, token):
        return self.request("logout", token=token)

    def create_user(self, token, name, group, pin):
        return self.request("create_user", token=token, name=name, group=group, pin=pin)

    def load_progress(self, token):
        return self.request("load_progress", token=token)

    def save_progress(self, token, progress, expected_revision, operation_id):
        return self.request("save_progress", token=token, progress=progress, expected_revision=expected_revision, operation_id=operation_id)

    def get_lists(self):
        return self.request("get_lists")

    def save_lists(self, token, lists):
        return self.request("save_lists", token=token, lists=lists)

    def students(self, token):
        return self.request("students", token=token)

    def import_progress(self, token, student_id, progress, expected_revision):
        return self.request("import_progress", token=token, student_id=student_id, progress=progress, expected_revision=expected_revision)
