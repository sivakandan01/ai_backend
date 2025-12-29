from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class Session(BaseModel):
    id: str
    user_id: str
    type: Literal["message", "mermaid", "image"]
    session_name: str
    date: datetime

class CreateSession(BaseModel):
    user_id: str
    session_name: str

class UpdateSession(BaseModel):
    session_name: str

class SessionResponse(BaseModel):
    id: str
    session_name: str