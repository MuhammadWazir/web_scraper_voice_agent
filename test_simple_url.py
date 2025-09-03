# poll_example.py
import asyncio
import httpx
import time

async def poll(job_url: str):
    async with httpx.AsyncClient() as client:
        start = time.monotonic()
        while True:
            if time.monotonic() - start > 60:
                print("Timeout waiting for job")
                return
            resp = await client.get(job_url, headers={
                "Authorization": "Bearer fc-d17da6d51f7f4e81a25c7ec5a07a5e8f"
            })
            print("GET status:", resp.status_code)
            data = resp.json()
            print("JOB:", data)
            if data.get("status") == "completed":
                # 👇 Firecrawl usually puts scraped data in data["data"]
                print("DONE. Pages:", len(data.get("data", [])))
                if data.get("data"):
                    print("First page text:", data["data"][0].get("text", "")[:500])
                return
            await asyncio.sleep(2)

if __name__ == "__main__":
    job_url = "https://api.firecrawl.dev/v1/crawl/0a329215-fe7e-43aa-9865-124bb2714c04"
    asyncio.run(poll(job_url))
