import os
import streamlit as st
from services.database import LocalDatabase, ServiceError
from services.gsheets import SheetsDatabase


def setting(name, default=""):
    try:
        return os.environ.get(name, st.secrets.get(name, default))
    except FileNotFoundError:
        return os.environ.get(name, default)


def database():
    backend = setting("BACKEND", "sqlite")
    if backend == "gsheets":
        return SheetsDatabase(setting("GSHEETS_URL"), setting("GSHEETS_API_KEY"))
    if backend == "sqlite":
        return LocalDatabase(setting("DATABASE_PATH", "runtime/glosflow.sqlite3"), setting("ADMIN_PASSWORD"))
    raise ServiceError("BACKEND måste vara sqlite eller gsheets.")


@st.cache_data(ttl=600, show_spinner=False)
def _cached_lists(source):
    return database().get_lists()


def shared_lists():
    """Lärarens listor hämtas en gång och delas av alla elever i tio minuter.

    Tidigare hämtade varje ny elev listorna från databasen, vilket tar någon sekund med
    Google Sheets. Läraren tömmer cachen när en lista ändras, så ändringar syns direkt.
    """
    source = (setting("BACKEND", "sqlite"), setting("GSHEETS_URL"), setting("DATABASE_PATH", "runtime/glosflow.sqlite3"))
    return _cached_lists(source)


def lists_changed():
    _cached_lists.clear()
