from pydantic import BaseModel, Field
from typing import Optional

class StormRequest(BaseModel):
    """Request model for STORM queries."""
    topic: str
    stream: bool = False
    
class StormResponse(BaseModel):
    """Response model for STORM results."""
    result: str

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    timestamp: str
    uptime: Optional[int] = None