from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from app.helpers.auth import check_for_auth
from .schema import CreateChats, UpdateChats, ChatResponse, ConversationResponse
from app.helpers.dependencies import get_chat_service
from app.core.socket_manager import manager
from typing import List

router = APIRouter(prefix="/chats", tags=["chats"])

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(request: Request, service = Depends(get_chat_service), _ = Depends(check_for_auth)):
    user = request.state.user
    result = await service.fetch_conversations(user.get("id"))
    return result

@router.post("/")
async def create_chats(chats: CreateChats, request: Request, service = Depends(get_chat_service), _ = Depends(check_for_auth)):
    user = request.state.user
    result, is_new = await service.create_chat(chats, user)
    
    if result:
        payload = {
            "type": "new_message",
            "message": result,
            "is_new_conversation": is_new
        }
        await manager.send_personal_message(payload, chats.receiver_id)
        
    return result

@router.get("/{receiver_id}", response_model=List[ChatResponse])
async def get_chats(receiver_id: str, request: Request, service = Depends(get_chat_service), _ = Depends(check_for_auth)):
    user = request.state.user
    result = await service.fetch_chat(receiver_id, user)
    return result

@router.put("/{chat_id}")
async def update_chats(chat_id: str, chats: UpdateChats, request: Request, service = Depends(get_chat_service), _ = Depends(check_for_auth)):
    user = request.state.user
    result = await service.update_chat(chat_id, chats, user)
    return result