from fastapi import APIRouter, HTTPException
from services.elevenlabs_service import get_signed_url_service

router = APIRouter(prefix="", tags=["elevenlabs"])

@router.get("/signed-url")
async def get_signed_url():
	try:
		return await get_signed_url_service()
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


