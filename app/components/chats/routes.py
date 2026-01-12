from fastapi import APIRouter, Depends
from app.helpers.auth import check_for_auth
from .schema import CreateChats, UpdateChats, ChatResponse
from app.helpers.dependencies import get_chat_service

router = APIRouter(prefix="/chats", tags=["chats"], dependencies=[Depends(check_for_auth)])

@router.post("/")
async def create_chats(chats: CreateChats, service = Depends(get_chat_service)):
    pass

