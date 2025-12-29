from fastapi import APIRouter, BackgroundTasks, Depends, Request
from .schema import CreateMessage, MessageResponse, Message
from .service import MessageService
from app.helpers.dependencies import get_message_service
from typing import List
from app.helpers.auth import check_for_auth

router = APIRouter(prefix="/message", tags=["message"], dependencies=[Depends(check_for_auth)])

@router.post("/", response_model=MessageResponse)
async def send_message(
    message: CreateMessage,
    background_tasks: BackgroundTasks,
    request: Request,
    service: MessageService = Depends(get_message_service)
):
    user = request.state.user
    result = await service.send_message(message, background_tasks, user)
    return result

@router.get("/{session_id}", response_model=List[Message])
async def get_messages(
    session_id: str,
    request: Request,
    service: MessageService = Depends(get_message_service)
):
    user = request.state.user
    result = await service.get_messages(session_id, user.get("id", ""))
    return result