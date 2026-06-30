from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_without_api_key_returns_503():
    response = client.post(
        "/api/v1/query",
        json={"question": "What is RAG?"},
    )
    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]
