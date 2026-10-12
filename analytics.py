import duckdb

DB_FILE = "metrics.duckdb"

def generate_report():
    conn = duckdb.connect(DB_FILE, read_only=True)

    # Check available tables in metrics.duckdb
    tables = [row[0] for row in conn.execute("SHOW TABLES").fetchall()]
    
    if not tables:
        print("❌ No tables found in metrics.duckdb. Make sure uvicorn has ingested at least one metric.")
        conn.close()
        return

    # Use the first available table (or default to 'metrics')
    target_table = tables[0]
    
    query = f"""
    SELECT 
        scraper_name,
        COUNT(*) AS total_runs,
        ROUND(AVG(response_time_ms), 2) AS avg_latency_ms,
        SUM(items_extracted) AS total_extracted,
        SUM(items_failed) AS total_failed,
        MAX(timestamp) AS last_run
    FROM {target_table}
    GROUP BY scraper_name
    ORDER BY last_run DESC;
    """

    try:
        results = conn.execute(query).fetchall()
        print(f"\n📊 SCRAPER PIPELINE SUMMARY (Table: '{target_table}')")
        print("=" * 75)
        print(f"{'Scraper Name':<22} | {'Runs':<5} | {'Avg Latency':<12} | {'Extracted':<10} | {'Failed':<6}")
        print("-" * 75)

        for row in results:
            scraper, runs, avg_lat, extracted, failed, _ = row
            print(f"{scraper:<22} | {runs:<5} | {round(avg_lat, 1):<10}ms | {extracted:<10} | {failed:<6}")

        print("=" * 75 + "\n")
    except Exception as e:
        print(f"⚠️ Query error on table '{target_table}': {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    generate_report()