import pytest


@pytest.fixture(autouse=True)
def save_synchronously(monkeypatch):
    # I appen sparas framsteg i bakgrunden. Testerna väntar in sparningen så att de blir förutsägbara.
    monkeypatch.setenv('SAVE_WAIT', '30')
