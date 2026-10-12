import os
import pytest
import duckdb
from fastapi.testclient import TestClient
from main import app, DB_FILE

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    """Resets or isolates DuckDB state before running tests."""
    yield
    # Cleanup DuckDB test artifact if generated locally
    if os.path.exists(DB_FILE):
        conn = duckdb.connect(DB_FILE)
        conn.execute("DELETE FROM scraper_metrics WHERE scraper_name LIKE 'test_%'")
        conn.close()

def test_receive_metric_success():
    """Verify POST /api/v1/metrics correctly accepts valid scraper telemetry."""
    payload = {
        "scraper_name": "test_verification_bot",
        "response_time_ms": 1250.5,
        "http_status_code": 200,
        "items_extracted": 100,
        "items_failed": 0
    }
    response = client.post("/api/v1/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["scraper_name"] == "test_verification_bot"

def test_receive_metric_validation_error():
    """Verify POST /api/v1/metrics rejects invalid payloads."""
    payload = {
        "scraper_name": "test_invalid_bot",
        # Missing response_time_ms field
        "http_status_code": 200,
        "items_extracted": 10
    }
    response = client.post("/api/v1/metrics", json=payload)
    assert response.status_code == 422  # Unprocessable Entity

def test_get_summary_endpoint():
    """Verify GET /api/v1/summary returns non-empty structured data."""
    response = client.get("/api/v1/summary")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "data" in data
    assert isinstance(data["data"], list)