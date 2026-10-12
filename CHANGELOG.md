# Changelog

All notable changes to the Scraper Tracker pipeline will be documented in this file.

## [0.1.0] - 2026-10-12

### Added
- FastAPI ingestion endpoint `POST /api/v1/metrics` for scraper performance logging.
- DuckDB persistence backend with automatic schema generation (`scraper_metrics`).
- Asynchronous `alerts.py` evaluation engine triggering Telegram Markdown alerts on threshold breaches.
- Reusable `tracker_client.py` client and integration with `Crawl4AI`.
- Scraper-specific threshold overrides for latency, status codes, and item failure limits.
- Local `analytics.py` terminal summary generator with table auto-detection.