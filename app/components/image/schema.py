from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.constants.session import STATUS_SUCCESS

class Image(BaseModel):
    id: str
    image_url: str
    session_id: str
    is_success: bool
    prompt: str

class ImageResponse(BaseModel):
    image_url: str
    session_id: str
    status: str = STATUS_SUCCESS
    message: str = "Image generated successfully"

class CreateImage(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=1000, description="Image generation prompt")
    session_id: Optional[str] = Field(None, description="Session ID (creates new session if not provided)")

    @field_validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty or whitespace only')
        return ' '.join(v.split())