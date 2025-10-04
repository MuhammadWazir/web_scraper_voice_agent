from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time
from configs.config import load_settings
from helpers.scrape import scrape_website
from helpers.ai_processor import process_prompts, get_client_by_id, save_client_to_data_json
from dtos.voice_agent import VoiceAgentRequest, VoiceAgentResponse

app = FastAPI(title="Web Scraper Voice Agent", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = load_settings()

voice_agents = {}
chat_contexts = {}


@app.post("/create-voice-agent", response_model=VoiceAgentResponse)
async def create_voice_agent(
	request: VoiceAgentRequest):
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
	request_data = {
		"website_url": str(request.website_url),
		"target_audience": request.target_audience
	}
	
	save_success = await save_client_to_data_json(request_data, assets)
	if not save_success:
		print(f"Warning: Failed to save client data")
	
	time_end = time.time()
	print(f"Time taken: {time_end - time_start} seconds")
	return VoiceAgentResponse(
		session_id=session_id,
		assets=assets
	)

@app.get("/client/{client_id}")
async def get_client(client_id: str):
	"""Get client data by ID"""
	client_data = await get_client_by_id(client_id)
	if not client_data:
		raise HTTPException(status_code=404, detail="Client not found")
	return client_data

@app.get("/")
async def root():
	return {"message": "Voice Agent System Ready"}


if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000) 