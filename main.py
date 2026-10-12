from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from database import fetch_metrics, init_db, save_metric
from alerts import evaluate_and_alert

app = FastAPI(title="Scraper Pipeline Tracker")

# Initialize the database table on startup
init_db()

class ScraperMetric(BaseModel):
    scraper_name: str
    response_time_ms: float
    http_status_code: int
    items_extracted: int
    items_failed: int

@app.get("/")
def home():
    return {"message": "Scraper Pipeline Tracker API is running."}

@app.post("/api/v1/metrics")
async def record_metric(metric: ScraperMetric, background_tasks: BackgroundTasks):
    save_metric(metric)
    background_tasks.add_task(evaluate_and_alert, metric)
    print(f"Received metric from {metric.scraper_name}")
    return {"status": "success", "data": metric}

@app.get("/api/v1/metrics")
def get_metrics():
    data = fetch_metrics()
    return {"status": "success", "count": len(data), "data": data}