import asyncio
import duckdb
from alerts import send_telegram_alert

DB_FILE = "metrics.duckdb"

async def dispatch_daily_summary():
    """Queries DuckDB for 24 hour pipeline performance and sends a Telegram report."""
    conn = duckdb.connect(DB_FILE, read_only=True)

    # Detect active metrics table
    tables = [row[0] for row in conn.execute("SHOW TABLES").fetchall()]
    if not tables:
        print("No tables found in metrics.duckdb.")
        conn.close()
        return

    target_table = tables[0]

    query = f"""
    SELECT
        scraper_name,
        COUNT(*) AS total_runs, 
        ROUND(AVG(response_time_ms), 2) AS avg_latency_ms,
        SUM(items_extracted) AS total_extracted,
        SUM(items_failed) AS total_failed
    FROM {target_table}
    WHERE timestamp >= NOW() - INTERVAL '24 hours'
    GROUP BY scraper_name
    ORDER BY total_runs DESC;
    """

    results = conn.execute(query).fetchall()
    conn.close()

    if not results:
        msg = (
            "*24-Hour Scraper Pipeline Digest* \n\n"
            "No scraper executions recorded in the last 24 hours."  
        )   
        await send_telegram_alert(msg)
        return

    total_runs = sum(row[1] for row in results)
    total_extracted = sum(row[3] or 0 for row in results)
    total_failed = sum(row[4] or 0 for row in results)

    scraper_details = []
    for row in results:
        scraper_name, runs, avg_lat, extracted, failed = row
        ext_val = extracted or 0
        fail_val = failed or 0
        status_icon = "🟢" if fail_val == 0 else "🔴"

    scraper_details.append(
            f"{status_icon} *`{scraper_name}`*\n"
            f"   • Runs: `{runs}` | Avg Latency: `{round(avg_lat, 1)}ms`\n"
            f"   • Extracted: `{ext_val:,}` | Failed: `{fail_val:,}`"
        )

    formatted_bots = "\n\n".join(scraper_details)

    digest_message = (
        f"📊 *24-Hour Scraper Pipeline Digest* 📊\n\n"
        f"📈 *Pipeline Overview*\n"
        f"• Total Executions: `{total_runs}`\n"
        f"• Total Extracted: `{total_extracted:,}`\n"
        f"• Total Failed: `{total_failed:,}`\n\n"
        f"🤖 *Scraper Performance*\n\n"
        f"{formatted_bots}\n\n"
        f"⚙️ _Scraper Monitoring Pipeline_"
    )

    await send_telegram_alert(digest_message)


if __name__ == "__main__":
    asyncio.run(dispatch_daily_summary())