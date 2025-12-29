from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal

class Message(BaseModel):
    id: str
    content: Optional[str] = Field(None, description="Message content (None if error)")
    session_id: str
    role: Literal["user", "assistant"] = Field(..., description="Message sender role")
    date: datetime
    is_success: bool = Field(..., description="Whether message generation succeeded")

class CreateMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="User message content")
    session_id: Optional[str] = Field(None, description="Session ID (creates new session if not provided)")

    @field_validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty or whitespace only')
        return v.strip()

class MessageResponse(BaseModel):
    content: str
    role: str
    session_id: str
    is_success: bool