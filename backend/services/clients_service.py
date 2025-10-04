import uuid
import time
from helpers.scrape import scrape_website
from helpers.ai_processor import process_prompts
from repositories.clients_repository import add_client, load_all_clients, get_client_by_id


async def create_voice_agent_service(website_url: str, target_audience: str, company_name: str) -> dict:
	time_start = time.time()
	session_id = uuid.uuid4().hex

	website_content = await scrape_website(str(website_url))
	assets = await process_prompts(
		str(website_url),
		website_content,
		target_audience,
		"gpt-5",
	)

	request_data = {
		"website_url": str(website_url),
		"target_audience": target_audience,
	}

	save_success = add_client(request_data, assets, company_name)
	if not save_success:
		print("Warning: Failed to save client data")

	time_end = time.time()
	print(f"Time taken: {time_end - time_start} seconds")

	return {
		"session_id": session_id,
		"assets": assets,
	}


def get_all_clients_service() -> list[dict]:
	return load_all_clients()


def get_client_by_id_service(client_id: str) -> dict | None:
	return get_client_by_id(client_id)


