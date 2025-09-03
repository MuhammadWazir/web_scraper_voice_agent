import json
from fastapi import WebSocket


async def get_init_params(websocket: WebSocket) -> tuple[str, str]:
	params = dict(websocket.query_params)
	website_url = params.get("website")
	audience_context = params.get("audience")
	if website_url and audience_context:
		return website_url, audience_context
	# Expect a single init JSON message
	init_msg = await websocket.receive_text()
	try:
		init_obj = json.loads(init_msg)
	except json.JSONDecodeError:
		raise ValueError("Expected JSON init with fields: website, audience")
	website_url = website_url or init_obj.get("website")
	audience_context = audience_context or init_obj.get("audience")
	if not website_url or not audience_context:
		raise ValueError("Missing required fields: website and audience")
	return website_url, audience_context 