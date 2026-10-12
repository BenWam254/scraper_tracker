import duckdb

DB_FILE = "metrics.duckdb"

def init_db():
    """Creates the metric table if it doesn't already exist."""
    conn = duckdb.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scraper_metrics (
            scraper_name VARCHAR,
            response_time_ms DOUBLE,
            http_status_code INTEGER,
            items_extracted INTEGER,
            items_failed INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.close()

def save_metric(metric):
    """Inserts a new metric record into DuckDB."""
    conn = duckdb.connect(DB_FILE)
    conn.execute("""
        INSERT INTO scraper_metrics
        (scraper_name, response_time_ms, http_status_code, items_extracted, items_failed)
        VALUES (?, ?, ?, ?, ?)
    """, (
        metric.scraper_name, 
        metric.response_time_ms, 
        metric.http_status_code, 
        metric.items_extracted, 
        metric.items_failed
    ))
    conn.close()

def fetch_metrics():
    """Retrieves all metric records from DuckDB ordered by newest first."""
    conn = duckdb.connect(DB_FILE)
    columns = ["scraper_name", "response_time_ms", "http_status_code", "items_extracted", "items_failed", "timestamp"]
    rows = conn.execute("SELECT * FROM scraper_metrics ORDER BY timestamp DESC").fetchall()
    conn.close()

    # Pair column names with row values to return a list of dictionaries
    return [dict(zip(columns, row)) for row in rows]