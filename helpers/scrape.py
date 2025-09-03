import re
import httpx
import warnings
from crawl4ai import AsyncWebCrawler


async def scrape_with_crawl4ai(url: str, timeout_seconds: int) -> str:
	"""Use Crawl4AI to scrape the website and return aggregated text content."""
	# Suppress warnings during execution
	warnings.filterwarnings("ignore", category=ResourceWarning)
	
	crawler = AsyncWebCrawler()
	
	try:
		result = await crawler.arun(
			url=url,
			extraction_strategy="raw-html",
			llm_extraction=False
		)
		
		# Get the first result from the Crawl4AI response
		if hasattr(result, '_results') and result._results:
			first_result = result._results[0]
			
			# Combine content from different sources
			texts = []
			
			# Try markdown first (cleaner text)
			if hasattr(first_result, 'markdown') and first_result.markdown:
				texts.append(first_result.markdown)
			
			# Fallback to HTML if no markdown
			if not texts and hasattr(first_result, 'html') and first_result.html:
				# Clean HTML to get text
				html_text = re.sub(r"<script[\s\S]*?</script>", " ", first_result.html, flags=re.IGNORECASE)
				html_text = re.sub(r"<style[\s\S]*?</style>", " ", html_text, flags=re.IGNORECASE)
				html_text = re.sub(r"<[^>]+>", " ", html_text)
				html_text = re.sub(r"\s+", " ", html_text).strip()
				texts.append(html_text)
			
			# Try extracted content if available
			if hasattr(first_result, 'extracted_content') and first_result.extracted_content:
				if isinstance(first_result.extracted_content, dict):
					content = first_result.extracted_content.get("content") or first_result.extracted_content.get("main_text") or ""
					if content:
						texts.append(content)
				else:
					texts.append(str(first_result.extracted_content))
			
			combined = "\n\n".join(texts).strip()
			return combined if combined else "No content extracted"
		
		return "No results from Crawl4AI"
		
	except Exception as e:
		# Fallback to naive scraping if Crawl4AI fails
		return await naive_scrape_fallback(url, timeout_seconds)
	finally:
		# Force cleanup to prevent ResourceWarnings
		try:
			await crawler.aclose()
		except:
			pass


async def naive_scrape_fallback(url: str, timeout_seconds: int) -> str:
	"""Fallback to simple HTTP GET and HTML stripping."""
	async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
		resp = await client.get(url)
		resp.raise_for_status()
		html = resp.text
	text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
	text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
	text = re.sub(r"<[^>]+>", " ", text)
	return re.sub(r"\s+", " ", text).strip()


# Alias for backward compatibility with main.py
scrape_with_firecrawl = scrape_with_crawl4ai 