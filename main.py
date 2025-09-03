from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import json
import uuid

from configs.config import load_settings
from helpers.ws_init import get_init_params
from helpers.scrape import scrape_with_firecrawl
from helpers.prompts import compile_assets
from helpers.bridge import connect_elevenlabs_ws, bidirectional_bridge
from helpers.usage import CAMPAIGN_NAME, mark_session_start, mark_session_end

app = FastAPI(title="Web Scraper Voice Agent", version="1.0.0")

settings = load_settings()


@app.websocket("/session")
async def session(websocket: WebSocket):
	await websocket.accept()
	session_id = uuid.uuid4().hex
	started_at = mark_session_start(session_id)

	try:
		try:
			website_url, audience_context = await get_init_params(websocket)
		except ValueError as ve:
			await websocket.send_text(json.dumps({"type": "error", "message": str(ve)}))
			await websocket.close(code=1008)
			return

		try:
			website_text = await scrape_with_firecrawl(website_url, settings.scrape_timeout_seconds)
		except Exception as e:
			await websocket.send_text(json.dumps({"type": "error", "message": f"Failed to scrape website: {str(e)}"}))
			await websocket.close(code=1011)
			return

		assets = compile_assets(website_text, audience_context)
		await websocket.send_text(json.dumps({
			"type": "assets",
			"session_id": session_id,
			"campaign": CAMPAIGN_NAME,
			"website": website_url,
			"audience": audience_context,
			"assets": assets,
		}))

		if not settings.elevenlabs_api_key:
			await websocket.send_text(json.dumps({"type": "error", "message": "Server missing ELEVENLABS_API_KEY"}))
			await websocket.close(code=1011)
			return

		eleven_ws_url = settings.elevenlabs_ws_url
		headers = {"Authorization": f"Bearer {settings.elevenlabs_api_key}"}
		if settings.shared_agent_id:
			headers["x-agent-id"] = settings.shared_agent_id

		async with connect_elevenlabs_ws(eleven_ws_url, headers) as eleven_ws:
			init_payload = {
				"type": "session_init",
				"session_id": session_id,
				"campaign": CAMPAIGN_NAME,
				"audience": audience_context,
				"assets": assets,
			}
			try:
				await eleven_ws.send(json.dumps(init_payload))
			except Exception:
				pass

			await bidirectional_bridge(websocket, eleven_ws)

	except WebSocketDisconnect:
		pass
	except Exception as e:
		try:
			await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
		except Exception:
			pass
	finally:
		mark_session_end(session_id, started_at)
		try:
			await websocket.close()
		except Exception:
			pass


@app.get("/")
async def root():
	return {"message": "Hello world"}


if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000) 