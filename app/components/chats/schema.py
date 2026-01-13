from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Chats(BaseModel):
    id: str
    content: str
    sender_id: str
    receiver_id: str
    created_at: datetime
    status: str = "sent"
    is_read: bool = False
    is_user: bool = True

class CreateChats(BaseModel):
    content: str
    receiver_id: str
    is_user: bool

class UpdateChats(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    is_read: Optional[bool] = None

class ChatResponse(BaseModel):
    id: str
    content: str
    sender_id: str
    receiver_id: str
    created_at: datetime
    status: str
    is_read: bool
    is_user: bool

class ConversationResponse(BaseModel):
    id: str
    user_name: str
    email: str
    last_message: str
    last_message_date: datetime