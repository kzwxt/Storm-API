from fastapi import APIRouter
from api.models import StormRequest, StormResponse
from api.service import StormService

router = APIRouter()

service = StormService()

@router.post("/query", response_model=StormResponse)
async def query(req: StormRequest):
    """Generate an article about the given topic."""

    result = service.run(req.topic)
    
    return StormResponse(result=result)