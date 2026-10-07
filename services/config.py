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
