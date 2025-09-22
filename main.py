from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
import uuid
import json
import time
from configs.config import load_settings
from helpers.scrape import scrape_website
from helpers.ai_processor import process_prompts
from helpers.chat_ai import generate_response
from dtos.voice_agent import VoiceAgentRequest, VoiceAgentResponse

app = FastAPI(title="Web Scraper Voice Agent", version="1.0.0")

settings = load_settings()

voice_agents = {}
chat_contexts = {}


@app.post("/create-voice-agent", response_model=VoiceAgentResponse)
async def create_voice_agent(request: VoiceAgentRequest):
	time_start = time.time()
	session_id = uuid.uuid4().hex
	website_content = await scrape_website(str(request.website_url))
	
	assets = await process_prompts(
		str(request.website_url),
		website_content,
		request.target_audience,
		"gpt-5"
	)
	
	voice_agents[session_id] = {
		"website_url": str(request.website_url),
		"website_content": website_content,
		"target_audience": request.target_audience,
		"assets": assets
	}
	time_end = time.time()
	print(f"Time taken: {time_end - time_start} seconds")
	return VoiceAgentResponse(
		session_id=session_id,
		assets=assets
	)


@app.websocket("/chat/{session_id}")
async def chat_with_agent(websocket: WebSocket, session_id: str):
	await websocket.accept()
	
	# Check if agent exists
	if session_id not in voice_agents:
		raise HTTPException(status_code=404, detail="Voice agent not found")
	
	if session_id not in chat_contexts:
		chat_contexts[session_id] = []
	
	agent_data = voice_agents[session_id]
	
	await websocket.send_text(json.dumps({
		"type": "agent_ready",
		"message": f"Hi! I'm your assistant for {agent_data['website_url']}. How can I help you today?"
	}))
	
	try:
		while True:
			data = await websocket.receive_text()
			message = json.loads(data)
			
			if message.get("type") == "user_message":
				user_text = message.get("text", "")
				
				# Add user message to context
				chat_contexts[session_id].append({"type": "user", "text": user_text})
				
				# Generate intelligent response
				ai_response = await generate_response(
					settings.openai_api_key,
					agent_data,
					chat_contexts[session_id],
					user_text
				)
				
				# Add agent response to context
				chat_contexts[session_id].append({"type": "agent", "text": ai_response})
				
				response = {
					"type": "agent_response", 
					"text": ai_response
				}
				
				await websocket.send_text(json.dumps(response))
				
	except WebSocketDisconnect:
		pass
	except Exception as e:
		print(f"WebSocket error: {e}")
	finally:
		try:
			await websocket.close()
		except:
			pass


@app.get("/")
async def root():
	return {"message": "Voice Agent System Ready"}


if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000) 