import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    with TestClient(app) as c:   # "with" runs the startup code (creates tables)
        yield c