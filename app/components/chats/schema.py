from pydantic import BaseModel
from typing import Optional

class Chats(BaseModel):
    id: str
    content: str
    sender_id: str
    receiver_id: str
    created_at: str
    status: str
    is_read: bool
    is_user: bool

class CreateChats(BaseModel):
    content: str
    sender_id: str
    receiver_id: str
    is_user: bool

class UpdateChats(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    is_read: Optional[bool]

class ChatResponse(BaseModel):
    id: str
    content: str
    created_at: str
    status: str
    is_read: bool
    is_user: bool