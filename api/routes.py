import time

from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from api.models import StormRequest, StormResponse, HealthResponse
from core.storm_service import StormService
from datetime import datetime
from utils.logging_config import get_logger
from utils.middleware import get_request_id


router = APIRouter()
logger = get_logger(__name__)

_storm_service = StormService()

def get_storm_service() -> StormService:
    """Return the singleton StormService instance."""
    return _storm_service

def get_uptime() -> int:
    """Calculate server uptime in seconds."""
    from main import START_TIME
    return int(time.time() - START_TIME)

def check_environment() -> bool:
    """Check if required environment variables are set."""
    import os
    required_vars = ["DEEPSEEK_API_KEY", "SERPER_API_KEY"]
    return all(os.getenv(var) for var in required_vars)

def check_storm_service() -> bool:
    """Check if StormService is initialized and working."""
    try:
        service = get_storm_service()
        return hasattr(service, 'lm_configs') and hasattr(service, 'retriever')
    except Exception:
        return False

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    request_id = get_request_id()
    env_ok = check_environment()
    service_ok = check_storm_service()
    status = "healthy" if env_ok and service_ok else "unhealthy"

    logger.info(
        "Health check performed",
        extra={
            "event": "health_check",
            "request_id": request_id,
            "status": status,
            "env_ok": env_ok,
            "service_ok": service_ok
        }
    )

    return HealthResponse(
        status=status,
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat() + "Z",
        uptime=get_uptime()
    )

async def stream_article_generator(topic: str, service: StormService):
    """Async generator that streams article generation progress."""
    try:
        for chunk in service.run_with_streaming(topic):
            yield chunk
    except Exception as e:
        yield f"❌ Error: {str(e)}\n"


@router.post("/query")
async def query(req: StormRequest, service: StormService = Depends(get_storm_service)):
    """Generate an article using STORM pipeline."""
    request_id = get_request_id()
    logger.info(
        "Query request received",
        extra={
            "event": "query_request_received",
            "request_id": request_id,
            "topic": req.topic,
            "stream": req.stream
        }
    )

    try:
        if req.stream:
            return StreamingResponse(
                stream_article_generator(req.topic, service),
                media_type="text/plain"
            )
        else:
            result = service.run(req.topic)
            return StormResponse(result=result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"STORM generation failed: {str(e)}"
        )

@router.post("/query/stream")
async def query_stream(req: StormRequest, service: StormService = Depends(get_storm_service)):
    """Stream article generation progress and result."""
    request_id = get_request_id()

    logger.info(
        "Stream request received",
        extra={
            "event": "stream_request_received",
            "request_id": request_id,
            "topic": req.topic
        }
    )

    return StreamingResponse(
        stream_article_generator(req.topic, service),
        media_type="text/plain"
    )
