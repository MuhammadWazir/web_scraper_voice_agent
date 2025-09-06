import re
import httpx
import warnings
from crawl4ai import AsyncWebCrawler


async def scrape_website(url: str, timeout_seconds: int) -> str:
	async with AsyncWebCrawler() as crawler:
		result = await crawler.arun(
			url=url,
			extraction_strategy="raw-html",
			llm_extraction=False
		)
		return result.html
