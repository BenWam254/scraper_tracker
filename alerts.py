import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Default fallback rules
DEFAULT_THRESHOLDS = {
    "max_latency_ms": 2000.0,
    "allowed_status_codes": [200, 201],
    "max_failed_items": 0,
}

# Per-scraper rule overrides
SCRAPER_THRESHOLDS = {
    "hn_top_stories": {
        "max_latency_ms": 7000.0,  # Browser rendering gets a higher latency allowance
        "allowed_status_codes": [200],
        "max_failed_items": 0,
    },
    "fast_api_scraper": {
        "max_latency_ms": 800.0,
        "allowed_status_codes": [200],
        "max_failed_items": 0,
    },
}


async def send_telegram_alert(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials missing. Alert dispatch skipped.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(url, json=payload, timeout=5.0)
            if res.status_code != 200:
                print(f"Failed to dispatch Telegram alert: {res.status_code} {res.text}")
        except Exception as e:
            print(f"Failed to dispatch Telegram alert: {e}")


async def evaluate_and_alert(metric):
    """Evaluates metrics against scraper-specific or default rules."""
    rules = SCRAPER_THRESHOLDS.get(metric.scraper_name, DEFAULT_THRESHOLDS)
    issues = []

    # Latency check
    if metric.response_time_ms > rules["max_latency_ms"]:
        issues.append(
            f"⚠️ High Latency: {metric.response_time_ms}ms (Limit: {rules['max_latency_ms']}ms)"
        )

    # HTTP Status check
    if metric.http_status_code not in rules["allowed_status_codes"]:
        issues.append(f"❌ HTTP Status Error: {metric.http_status_code}")

    # Item failure check
    if metric.items_failed > rules["max_failed_items"]:
        total = metric.items_extracted + metric.items_failed
        issues.append(f"🔻 Failed Items: {metric.items_failed} failed out of {total}")

    if issues:
        print(f"[ALERT TRIGGERED] Scraper: {metric.scraper_name}")
        issues_formatted = "\n".join(issues)
        alert_msg = (
            f"🚨 *Scraper Pipeline Alert* 🚨\n\n"
            f"*Scraper:* `{metric.scraper_name}`\n"
            f"*Issues Detected:*\n{issues_formatted}"
        )
        await send_telegram_alert(alert_msg)