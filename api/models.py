from pydantic import BaseModel, Field, field_validator
from typing import Optional

class StormRequest(BaseModel):
    """Request model for STORM queries."""
    topic: str = Field(
        min_length=3,
        max_length=200,
        description="Research topic (3-200 characters)"
    )
    stream: bool = Field(default=False, description="Enable streaming mode")
    
    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate topic format and content."""
        v = v.strip()
        
        if not v:
            raise ValueError('Topic cannot be empty or whitespace')
        
        forbidden_patterns = ['<script>', 'javascript:', 'http://', 'https://']
        for pattern in forbidden_patterns:
            if pattern.lower() in v.lower():
                raise ValueError(f'Topic contains forbidden pattern: {pattern}')
        
        return v
    
class StormResponse(BaseModel):
    """Response model for STORM results."""
    result: str

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    timestamp: str
    uptime: Optional[int] = None