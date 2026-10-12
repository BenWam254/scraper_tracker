# Scraper Monitoring & Alert Pipeline

A lightweight, asynchronous monitoring service for web scrapers built with FastAPI, DuckDB, `httpx`, and Telegram Bot API.

## Features
- **Async Metric Ingestion**: High-throughput REST API with zero-latency background task processing.
- **DuckDB Storage**: Embedded OLAP database for fast metric querying.
- **Real-Time Telegram Alerts**: Instant notifications for threshold breaches (latency spikes, HTTP errors, failed items).
- **Per-Scraper Configuration**: Custom rules tailored for heavy browser tasks (e.g., Crawl4AI) vs. lightweight API scrapers.
- **CLI Analytics**: Terminal-based performance reports.

## Getting Started

1. **Install Dependencies**:
   ```bash
   uv sync
   uv run crawl4ai-setup