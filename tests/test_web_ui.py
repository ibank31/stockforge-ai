from fastapi.testclient import TestClient

from stockforge import web_app


def test_home_contains_end_to_end_v2_workflow_controls():
    response = TestClient(web_app.app).get("/")
    assert response.status_code == 200
    body = response.text
    for marker in ("Upload &amp; analyze", "Analyze &amp; create plan", "Queue generation", "/api/jobs/", "similarity decision"):
        assert marker in body
    assert "human review" in body.lower()
