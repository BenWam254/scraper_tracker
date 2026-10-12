# scraper-tracker

An asynchronous monitoring and alerting pipeline built to track web scraper execution latency, status codes, and extraction metrics in real time.

Built with **FastAPI** for high-throughput metric ingestion and **DuckDB** for zero-maintenance embedded analytical persistence, `scraper-tracker` evaluates incoming run payloads against customizable per-bot rule thresholds and dispatches actionable alerts via the **Telegram Bot API**.

---

## Features

- **Fast Metric Ingestion:** RESTful endpoint (`POST /api/v1/metrics`) powered by FastAPI and Pydantic validation.
- **Non-Blocking Alert Dispatch:** Offloads rule evaluation and HTTP notifications to background tasks without delaying scraper execution.
- **Embedded Analytics:** Embedded DuckDB persistence paired with a CLI tool (`analytics.py`) supporting time-window filtering, failure auditing, and target scraper inspection.
- **Per-Scraper Thresholds:** Configurable failure rates, HTTP status codes, and latency limits tailored to lightweight API scrapers or heavy browser-rendered tasks (`crawl4ai`).
- **REST Summary Endpoint:** Programmatic API (`GET /api/v1/summary`) providing real-time aggregate pipeline statistics across all scrapers.

---

## Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** [DuckDB](https://duckdb.org/)
- **Package Manager:** [`uv`](https://github.com/astral-sh/uv)
- **Scraper Engine:** [Crawl4AI](https://github.com/unclecode/crawl4ai)
- **Alerting:** Telegram Bot API
- **Language:** Python 3.12+

---

## Project Structure

```text
scraper-tracker/
├── main.py              # FastAPI server & metric endpoints
├── alerts.py            # Alert rules engine & Telegram notifier
├── tracker_client.py    # Reusable client helper for scrapers
├── run_scraper.py       # Crawl4AI integration script
├── analytics.py         # CLI reporting & database query tool
├── metrics.duckdb       # Local DuckDB database file (git-ignored)
├── .env.example         # Template for environment credentials
├── .gitignore           # Git ignore configurations
├── CHANGELOG.md         # Version release history
└── README.md            # Documentation
```

## Getting Started

### 1. Prerequisites

Ensure you have **Python 3.12+** and **`uv`** installed on your machine.

If you don't have `uv` installed, run:

```bash
# macOS/Linux
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
```

### 2. Clone the Repository

Enter:

 ```bash
 git clone [https://github.com/BenWam254/scraper-tracker.git](https://github.com/BenWam254/scraper-tracker.git)
 cd scraper-tracker into your repository
```

### 3. Environment Setup

Create an .env file in the root directory:

```bash
cp .env.example .env
```
Edit .env to include your actual Telegram bot credentials:

```bash
TELEGRAM_BOT_TOKEN="your_telegram_bot_taken_here"
TELEGRAM_BOT_ID="your_telegram_chat_id_here"
```

### 4. Install Dependencies

Install dependencies into an isolated virtual environment using uv:

```bash
uv sync
```
If using crawl4ai for browser scraping, install Playwright's headless browser binaries:

```bash
uv run crawl4ai-setup
```
### 5. Usage

#### Start the Monitoring Server
Launch the FastAPI ingestion server locally:

```bash
uv run uvicorn main:app --reload
```
The server will start at http://127.0.0.1:8000. Explore interactive API documentation at http://127.0.0.1:8000/docs


#### Run a Scraper Test
In a second terminal window, run the example Crawl4AI scraper script:

```bash
uv run python run_scraper.py
```

### Run CLI Analytics
Query DuckDB execution history from your terminal using analytics.py:

```bash
# General pipeline summary
uv run python analytics.py
```
# Filter by time window (e.g., last 24 hours)

```bash
uv run python analytics.py --scraper hn_top_stories
```
# Show only failed runs or error responses

```bash
uv run python analytics.py --failed-only
```
### License
Distributed under the MIT License. See LICENSE for more information.
