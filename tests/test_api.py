from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_extension():
    response = client.post(
        "/api/files/",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
