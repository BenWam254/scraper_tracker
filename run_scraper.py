import asyncio
import time
from crawl4ai import AsyncWebCrawler
from tracker_client import log_scrape_run

async def scrape_target(url: str, scraper_name: str = "crawl4ai_universal"):
    start_time = time.time()
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        
        status_code = 200 if result.success else 500
        # Updated for Crawl4AI 0.9.x+
        extracted_count = len(result.markdown.raw_markdown) if (result.success and result.markdown) else 0
        failed_count = 0 if result.success else 1
        
        await log_scrape_run(
            scraper_name=scraper_name,
            start_time=start_time,
            status_code=status_code,
            items_extracted=extracted_count,
            items_failed=failed_count
        )

if __name__ == "__main__":
    asyncio.run(scrape_target("https://news.ycombinator.com", "hn_top_stories"))