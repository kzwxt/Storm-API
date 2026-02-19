"""
API Routes Module

This module defines all HTTP endpoints for the STORM API service.
It handles article generation queries, streaming responses, and health checks.

Endpoints:
    - GET /health: Health check endpoint
    - POST /query: Generate article (sync or streaming)
    - POST /query/stream: Stream article generation progress
"""

import time
from typing import AsyncGenerator, Union

from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from datetime import datetime

from api.models import StormRequest, StormResponse, HealthResponse
from core.storm_service import StormService
from utils.logging_config import get_logger
from utils.middleware import get_request_id


router = APIRouter()
logger = get_logger(__name__)

_storm_service: StormService = StormService()


def get_storm_service() -> StormService:
    """
    Return the singleton StormService instance.

    Returns:
        StormService: The shared service instance for STORM operations

    Example:
        >>> service = get_storm_service()
        >>> article = service.run("Python Programming")
    """
    return _storm_service


def get_uptime() -> int:
    """
    Calculate server uptime in seconds.

    Returns:
        int: Server uptime in seconds since application start

    Example:
        >>> uptime = get_uptime()
        >>> print(f"Server running for {uptime} seconds")
    """
    from main import START_TIME
    return int(time.time() - START_TIME)


def check_environment() -> bool:
    """
    Check if required environment variables are set.

    Returns:
        bool: True if all required environment variables are present, False otherwise

    Example:
        >>> is_configured = check_environment()
        >>> if not is_configured:
        ...     print("Missing required environment variables")
    """
    import os
    required_vars: list[str] = ["DEEPSEEK_API_KEY", "SERPER_API_KEY"]
    return all(os.getenv(var) for var in required_vars)


def check_storm_service() -> bool:
    """
    Check if StormService is initialized and working.

    Returns:
        bool: True if StormService is properly initialized, False otherwise

    Example:
        >>> is_healthy = check_storm_service()
        >>> print(f"STORM service healthy: {is_healthy}")
    """
    try:
        service: StormService = get_storm_service()
        return hasattr(service, 'lm_configs') and hasattr(service, 'retriever')
    except Exception:
        return False


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for monitoring.

    Returns:
        HealthResponse: Health status including version, timestamp, and uptime

    Example:
        >>> response = client.get("/health")
        >>> print(response.json())
        >>> {"status": "healthy", "version": "1.0.0", ...}
    """
    request_id: str = get_request_id()
    env_ok: bool = check_environment()
    service_ok: bool = check_storm_service()
    status: str = "healthy" if env_ok and service_ok else "unhealthy"

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


async def stream_article_generator(topic: str, service: StormService) -> AsyncGenerator[str, None]:
    """
    Async generator that streams article generation progress.

    Runs the STORM pipeline in a thread pool to avoid blocking the event loop.

    Args:
        topic: Research topic to generate article about
        service: StormService instance to run the pipeline

    Yields:
        str: Progress messages and article content chunks

    Raises:
        Exception: If STORM pipeline execution fails

    Example:
        >>> async for chunk in stream_article_generator("Python", service):
        ...     print(chunk)
    """
    try:
        # Run streaming in thread pool to avoid blocking event loop
        for chunk in await run_in_threadpool(service.run_with_streaming, topic):
            yield chunk
    except Exception as e:
        yield f"❌ Error: {str(e)}\n"


@router.post("/query")
async def query(req: StormRequest, service: StormService = Depends(get_storm_service)):
    """
    Generate an article using STORM pipeline.

    Args:
        req: StormRequest containing topic and streaming flag
        service: StormService instance (injected via dependency injection)

    Returns:
        StreamingResponse | StormResponse: Either a streaming response or
            complete article response based on req.stream flag

    Raises:
        HTTPException: If STORM generation fails with 500 status code

    Example:
        >>> # Non-streaming
        >>> response = client.post("/query", json={"topic": "Python", "stream": False})
        >>> print(response.json()["result"])

        >>> # Streaming
        >>> response = client.post("/query", json={"topic": "Python", "stream": True})
        >>> for chunk in response.stream_bytes():
        ...     print(chunk.decode())
    """
    request_id: str = get_request_id()
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
            # Run STORM in thread pool to avoid blocking event loop
            result: str = await run_in_threadpool(service.run, req.topic)
            return StormResponse(result=result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"STORM generation failed: {str(e)}"
        )


@router.post("/query/stream")
async def query_stream(req: StormRequest, service: StormService = Depends(get_storm_service)) -> StreamingResponse:
    """
    Stream article generation progress and result.

    Args:
        req: StormRequest containing topic
        service: StormService instance (injected via dependency injection)

    Returns:
        StreamingResponse: Streaming response with progress updates and article

    Example:
        >>> response = client.post("/query/stream", json={"topic": "Python"})
        >>> for chunk in response.stream_bytes():
        ...     print(chunk.decode())
    """
    request_id: str = get_request_id()

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
