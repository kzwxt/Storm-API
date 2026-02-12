from pydantic import BaseModel, Field
from typing import Optional

class StormRequest(BaseModel):
    topic: str
    stream: bool = False
    
class StormResponse(BaseModel):
    """Response model for STORM results"""
    result: str
