import time
import httpx

TRACKER_API_URL = "http://127.0.0.1:8000/api/v1/metrics"

async def log_scrape_run(
        scraper_name: str,
        start_time: float,
        status_code: int,
        items_extracted: int, 
        items_failed: int,
):
    """Calculates execution latency and posts pipeline performance metrics to the tracker API."""
    duration_ms = (time.time() - start_time) * 1000

    payload = {
        "scraper_name": scraper_name,
        "response_time_ms": round(duration_ms, 2),
        "http_status_code": status_code,
        "items_extracted": items_extracted,
        "items_failed": items_failed,
    }

    async with httpx.AsyncClient() as client:
        try:
            response =await client.post(TRACKER_API_URL, json=payload, timeout=5.0)
            if response.status_code == 200:
                print(f" metrics logged successfully for '{scraper_name}' ({round(duration_ms, 1)}ms)")
        except Exception as e:
            print(f" Could not reach metric server: {e}")