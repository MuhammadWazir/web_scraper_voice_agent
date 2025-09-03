import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from a local .env file if present
load_dotenv()


@dataclass(frozen=True)
class Settings:
	"""Application settings loaded from environment variables."""
	elevenlabs_api_key: str
	elevenlabs_model_id: str
	shared_agent_id: Optional[str]
	app_env: str
	scrape_timeout_seconds: int
	websocket_idle_timeout_seconds: int
	firecrawl_api_key: str
	firecrawl_api_url: str
	elevenlabs_ws_url: str


def load_settings() -> Settings:
	"""Load and validate application settings from environment variables."""
	elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "")
	elevenlabs_model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
	shared_agent_id = os.getenv("ELEVENLABS_SHARED_AGENT_ID")
	app_env = os.getenv("APP_ENV", "development")

	scrape_timeout_seconds = int(os.getenv("SCRAPE_TIMEOUT_SECONDS", "20"))
	websocket_idle_timeout_seconds = int(os.getenv("WEBSOCKET_IDLE_TIMEOUT_SECONDS", "300"))

	firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY", "")
	firecrawl_api_url = os.getenv("FIRECRAWL_API_URL", "https://api.firecrawl.dev/v1")

	from typing import List
	missing: List[str] = []
	# ElevenLabs key is optional for scraper tests; enforce at websocket connect time
	if not firecrawl_api_key:
		missing.append("FIRECRAWL_API_KEY")
	if missing:
		raise RuntimeError(
			"Missing required environment variables: " + ", ".join(missing)
		)

	elevenlabs_ws_url = os.getenv(
		"ELEVENLABS_WS_URL",
		f"wss://api.elevenlabs.io/v1/realtime?model_id={elevenlabs_model_id}",
	)

	return Settings(
		elevenlabs_api_key=elevenlabs_api_key,
		elevenlabs_model_id=elevenlabs_model_id,
		shared_agent_id=shared_agent_id,
		app_env=app_env,
		scrape_timeout_seconds=scrape_timeout_seconds,
		websocket_idle_timeout_seconds=websocket_idle_timeout_seconds,
		firecrawl_api_key=firecrawl_api_key,
		firecrawl_api_url=firecrawl_api_url,
		elevenlabs_ws_url=elevenlabs_ws_url,
	) 