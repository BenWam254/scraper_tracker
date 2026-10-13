import os
import pytest
import duckdb
from unittest.mock import patch
from fastapi.testclient import TestClient

from main import app, DB_FILE
from database import init_db  # Ensures table schema is initialized

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_clean_db():
    """Ensures database schema exists and cleans up test artifacts."""
    # 1. Initialize schema before running test
    init_db()
    
    yield
    
    # 2. Cleanup test entries safely
    if os.path.exists(DB_FILE):
        conn = duckdb.connect(DB_FILE)
        try:
            conn.execute("DELETE FROM scraper_metrics WHERE scraper_name LIKE 'test_%'")
        except duckdb.CatalogException:
            pass
        finally:
            conn.close()

@pytest.fixture(autouse=True)
def mock_telegram():
    """Mock Telegram alerts so CI tests never attempt external API calls."""
    with patch("alerts.send_telegram_alert") as mock_alert:
        yield mock_alert

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

def test_receive_metric_validation_error():
    """Verify POST /api/v1/metrics rejects invalid payloads."""
    payload = {
        "scraper_name": "test_invalid_bot",
        "http_status_code": 200,
        "items_extracted": 10
    }
    response = client.post("/api/v1/metrics", json=payload)
    assert response.status_code == 422

def test_get_summary_endpoint():
    """Verify GET /api/v1/summary returns non-empty structured data."""
    response = client.get("/api/v1/summary")
    assert response.status_code == 200
    assert "data" in response.json()