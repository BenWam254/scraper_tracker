import duckdb
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from alerts import evaluate_and_alert
from daily_summary import dispatch_daily_summary

DB_FILE = "metrics.duckdb"
scheduler = AsyncIOScheduler()


def init_db():
    conn = duckdb.connect(DB_FILE)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scraper_metrics (
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            scraper_name VARCHAR,
            response_time_ms DOUBLE,
            http_status_code INTEGER,
            items_extracted INTEGER,
            items_failed INTEGER
        )
    """
    )
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB & Start Scheduler
    init_db()

    # Schedule daily summary digest at 08:00 AM
    scheduler.add_job(dispatch_daily_summary, "cron", hour=8, minute=0)

    scheduler.start()
    print("⏰ APScheduler initialized: Daily summary scheduled for 08:00 AM.")

    yield

    # Shutdown: Cleanly stop scheduler
    scheduler.shutdown()
    print("🛑 APScheduler stopped.")


app = FastAPI(title="Scraper Tracker API", version="0.1.0", lifespan=lifespan)


class MetricPayload(BaseModel):
    scraper_name: str
    response_time_ms: float
    http_status_code: int
    items_extracted: int
    items_failed: int


@app.post("/api/v1/metrics")
async def receive_metric(metric: MetricPayload, background_tasks: BackgroundTasks):
    conn = duckdb.connect(DB_FILE)
    conn.execute(
        """
        INSERT INTO scraper_metrics 
        (scraper_name, response_time_ms, http_status_code, items_extracted, items_failed)
        VALUES (?, ?, ?, ?, ?)
    """,
        (
            metric.scraper_name,
            metric.response_time_ms,
            metric.http_status_code,
            metric.items_extracted,
            metric.items_failed,
        ),
    )
    conn.close()

    background_tasks.add_task(evaluate_and_alert, metric)
    return {"status": "success", "data": metric}


@app.get("/api/v1/summary")
async def get_summary():
    """Returns aggregated pipeline metrics across all scrapers."""
    try:
        conn = duckdb.connect(DB_FILE, read_only=True)
        query = """
            SELECT 
                scraper_name,
                COUNT(*) AS total_runs,
                ROUND(AVG(response_time_ms), 2) AS avg_latency_ms,
                SUM(items_extracted) AS total_extracted,
                SUM(items_failed) AS total_failed,
                MAX(timestamp) AS last_run
            FROM scraper_metrics
            GROUP BY scraper_name
            ORDER BY last_run DESC;
        """
        results = conn.execute(query).fetchall()
        conn.close()

        summary = [
            {
                "scraper_name": row[0],
                "total_runs": row[1],
                "avg_latency_ms": row[2],
                "total_extracted": row[3],
                "total_failed": row[4],
                "last_run": str(row[5]),
            }
            for row in results
        ]
        return {"status": "success", "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))