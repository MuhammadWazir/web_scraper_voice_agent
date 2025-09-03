import re
import httpx

from configs.config import load_settings


def aggregate_text_from_firecrawl_response(data: dict) -> str:
	texts = []
	if isinstance(data, dict):
		pages = data.get("pages")
		if isinstance(pages, list):
			for page in pages:
				text = page.get("text") or page.get("content") or page.get("markdown") or ""
				if isinstance(text, str):
					texts.append(text)
		elif isinstance(data.get("text"), str):
			texts.append(data["text"])
	return "\n\n".join(texts).strip()


async def scrape_with_firecrawl(url: str, timeout_seconds: int) -> str:
	settings = load_settings()
	headers = {
		"Authorization": f"Bearer {settings.firecrawl_api_key}",
		"Content-Type": "application/json",
	}
	payload = {"url": url}
	api_url = settings.firecrawl_api_url.rstrip("/") + "/crawl"
	async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
		resp = await client.post(api_url, json=payload, headers=headers)
		resp.raise_for_status()
		data = resp.json()
		return aggregate_text_from_firecrawl_response(data)


def naive_strip_html(html: str) -> str:
	text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
	text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
	text = re.sub(r"<[^>]+>", " ", text)
	return re.sub(r"\s+", " ", text).strip() 