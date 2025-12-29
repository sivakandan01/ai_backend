from pydantic import BaseModel, Field, field_validator
from typing import Optional

class Mermaid(BaseModel):
    id: str
    mermaid_code: str
    session_id: str
    is_success: bool
    prompt: str

class MermaidResponse(BaseModel):
    mermaid_code: str
    session_id: str
    diagram_id: str

class CreateMermaid(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500, description="Diagram description prompt")
    session_id: Optional[str] = Field(None, description="Session ID (creates new session if not provided)")

    @field_validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty or whitespace only')
        return v.strip()