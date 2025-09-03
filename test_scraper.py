import asyncio
import httpx
import time
from typing import List

firecrawl_api_key = "fc-d17da6d51f7f4e81a25c7ec5a07a5e8f"
firecrawl_api_url = "https://api.firecrawl.dev/v1"

def aggregate_text_from_firecrawl_response(data: dict) -> str:
    texts = []
    if not isinstance(data, dict):
        return ""
    # Firecrawl uses "data" array for pages
    pages = data.get("data") or data.get("pages") or []
    if isinstance(pages, list):
        for page in pages:
            # accept any of these fields
            text = page.get("text") or page.get("content") or page.get("markdown") or page.get("html") or ""
            if isinstance(text, str) and text.strip():
                texts.append(text.strip())
    # fallback top-level text
    if not texts and isinstance(data.get("text"), str) and data["text"].strip():
        texts.append(data["text"].strip())
    return "\n\n".join(texts).strip()

async def scrape_with_firecrawl(url: str, timeout_seconds: int = 120, poll_interval: float = 2.0) -> str:
    headers = {
        "Authorization": f"Bearer {firecrawl_api_key}",
        "Content-Type": "application/json",
        "User-Agent": "firecrawl-client/1.0 (+https://your.app)"
    }
    payload = {"url": url}
    api_url = firecrawl_api_url.rstrip("/") + "/crawl"

    collected_texts: List[str] = []
    seen_next_urls = set()

    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds + 10), follow_redirects=True) as client:
        # Create job
        resp = await client.post(api_url, json=payload, headers=headers)
        try:
            resp.raise_for_status()
        except Exception as e:
            print("POST /crawl failed:", resp.status_code, resp.text)
            raise

        job = resp.json()
        print("Created job:", job)
        job_id = job.get("id")
        if not job_id:
            raise RuntimeError("No job id in response: " + str(job))

        job_url = f"{api_url}/{job_id}"

        start = time.monotonic()
        backoff = poll_interval

        # Poll loop: try to collect anything available while waiting for completion
        while True:
            elapsed = time.monotonic() - start
            if elapsed > timeout_seconds:
                print(f"Timeout reached ({timeout_seconds}s). Returning collected data if any.")
                break

            try:
                status_resp = await client.get(job_url, headers=headers)
            except Exception as e:
                print("GET job_url failed:", e)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 1.5, 10.0)
                continue

            if status_resp.status_code != 200:
                print("Non-200 from job endpoint:", status_resp.status_code, status_resp.text[:500])
                await asyncio.sleep(backoff)
                backoff = min(backoff * 1.5, 10.0)
                continue

            data = status_resp.json()
            status = data.get("status") or data.get("state") or data.get("jobStatus")
            print(f"JOB STATUS: {status}  completed={data.get('completed')} total={data.get('total')}")

            # If data field already contains pages, aggregate them
            if data.get("data"):
                chunk = aggregate_text_from_firecrawl_response(data)
                if chunk:
                    print(f"Collected {len(chunk)} chars from job endpoint 'data' field.")
                    collected_texts.append(chunk)

            # If Firecrawl returned a 'next' URL, follow it (and follow pagination)
            next_url = data.get("next")
            while next_url:
                # avoid re-fetching same next url repeatedly
                if next_url in seen_next_urls:
                    break
                seen_next_urls.add(next_url)

                try:
                    next_resp = await client.get(next_url, headers=headers)
                except Exception as e:
                    print("GET next_url failed:", e)
                    break

                next_data = next_resp.json()
                # debug
                print("fetched next page; data length:", len(next_data.get("data") or []))
                chunk = aggregate_text_from_firecrawl_response(next_data)
                if chunk:
                    print(f"Appending {len(chunk)} chars from next page.")
                    collected_texts.append(chunk)
                next_url = next_data.get("next")

            # not done yet: wait and retry
            await asyncio.sleep(poll_interval)

    final_text = "\n\n".join(t for t in collected_texts if t).strip()
    if final_text:
        return final_text

    # if nothing collected, raise with helpful debug hint
    raise TimeoutError(
        "No scraped content collected. Debug hints: job status snapshot: "
        f"{job}."
    )


async def main():
    try:
        text = await scrape_with_firecrawl("https://www.python.org/", timeout_seconds=120, poll_interval=2.0)
        print("=== TEXT ===")
        print(text)
        print("=== END ===")
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    asyncio.run(main())
