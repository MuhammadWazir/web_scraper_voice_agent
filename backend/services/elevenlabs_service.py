import httpx
from configs.config import load_settings

settings = load_settings()


async def get_signed_url_service() -> dict:
	if not settings or not settings.xi_api_key:
		raise RuntimeError("XI_API_KEY not configured")

	eleven_api_url = f"https://api.elevenlabs.io/v1/convai/conversation/get_signed_url?agent_id={settings.agent_id}"

	async with httpx.AsyncClient(timeout=20) as client:
		resp = await client.get(
			eleven_api_url,
			headers={
				"xi-api-key": settings.xi_api_key,
			},
		)
	if resp.status_code != 200:
		raise RuntimeError(f"Failed to get signed URL: {resp.status_code} {resp.text}")
	data = resp.json()
	if not data or "signed_url" not in data:
		raise RuntimeError("Malformed response from ElevenLabs")
	return {"signed_url": data["signed_url"]}


