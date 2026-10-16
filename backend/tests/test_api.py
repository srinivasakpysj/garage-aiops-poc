import os
import tempfile

from fastapi.testclient import TestClient

# Set SQLite before importing the application settings/engine.
_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_db_file.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_db_file.name}"

from app.main import app  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_list_incident():
    create_response = client.post(
        "/api/v1/incidents",
        json={
            "source": "manual",
            "title": "Test CPU threshold",
            "severity": "high",
            "status": "open",
            "host_name": "poc-server-01",
            "summary": "Synthetic test incident",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Test CPU threshold"
    assert created["status"] == "open"

    list_response = client.get("/api/v1/incidents")
    assert list_response.status_code == 200
    assert any(item["id"] == created["id"] for item in list_response.json())


def test_reject_invalid_severity():
    response = client.post(
        "/api/v1/incidents",
        json={"title": "Invalid severity", "severity": "urgent"},
    )
    assert response.status_code == 422
