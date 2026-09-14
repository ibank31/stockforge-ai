from pathlib import Path

from fastapi.testclient import TestClient

from stockforge import web_app


def test_health():
    client = TestClient(web_app.app)
    assert client.get("/health").json()["status"] == "ok"


def test_upload_profiles_reference(tmp_path, monkeypatch):
    monkeypatch.setattr(web_app, "UPLOAD_ROOT", tmp_path / "uploads")
    from PIL import Image

    source = tmp_path / "reference.png"
    Image.new("RGB", (64, 64), "white").save(source)
    client = TestClient(web_app.app)
    with source.open("rb") as handle:
        response = client.post("/api/references", files={"file": ("reference.png", handle, "image/png")})
    assert response.status_code == 200
    assert response.json()["decision"] == "REVIEW_REQUIRED"
