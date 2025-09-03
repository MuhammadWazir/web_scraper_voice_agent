import asyncio
import warnings
from helpers.scrape import scrape_with_crawl4ai


async def main():
    # Suppress ResourceWarnings from Playwright cleanup
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
    try:
        url = "https://www.python.org/"
        print(f"Testing Crawl4AI scraping: {url}")
        
        text = await scrape_with_crawl4ai(url, 30)
        
        print("=== CRAWL4AI SCRAPED CONTENT ===")
        print(f"Length: {len(text)} characters")
        print("=== TEXT ===")
        print(text)
        print("=== END ===")
        
        
    except Exception as e:
        print("ERROR:", e)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        # Shutdown async generators to suppress the warnings
        loop = asyncio.get_event_loop()
        loop.run_until_complete(loop.shutdown_asyncgens())
