from fastapi import APIRouter, HTTPException
from services.clients_service import (
	create_voice_agent_service,
	get_all_clients_service,
	get_client_by_id_service,
)
from dtos.voice_agent import VoiceAgentRequest, VoiceAgentResponse

router = APIRouter(prefix="", tags=["clients"])


@router.get("/clients")
async def get_all_clients():
	"""Get all clients"""
	return get_all_clients_service()


@router.get("/client/{client_id}")
async def get_client(client_id: str):
	"""Get client data by ID"""
	client_data = get_client_by_id_service(client_id)
	if not client_data:
		raise HTTPException(status_code=404, detail="Client not found")
	return client_data

@router.post("/create-voice-agent", response_model=VoiceAgentResponse)
async def create_voice_agent(request: VoiceAgentRequest):
	result = await create_voice_agent_service(
		website_url=str(request.website_url),
		target_audience=request.target_audience,
		company_name=request.company_name,
	)
	return VoiceAgentResponse(
		client_id=result["client_id"],
	)

