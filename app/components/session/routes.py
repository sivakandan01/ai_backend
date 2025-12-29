from fastapi import APIRouter, Depends, Request
from app.helpers.auth import check_for_auth
from app.helpers.dependencies import get_session_service
from .service import SessionService
from .schema import SessionResponse, UpdateSession
from typing import List

router = APIRouter(prefix="/session", tags=["session"], dependencies=[Depends(check_for_auth)])

@router.get("/", response_model=List[SessionResponse])
async def get_sessions(
    request: Request,
    type: str,
    service: SessionService = Depends(get_session_service)
):
    user = request.state.user
    result = await service.fetch_sessions(user, type)
    return result

@router.post("/")
async def create_session(
    request: Request,
    service: SessionService = Depends(get_session_service)
):
    user = request.state.user
    name = "sample session"
    result = await service.create_session(user.get("id", ""), name, type="message")
    return result

@router.put("/{session_id}")
async def update_session(
    session_id: str,
    session_data: UpdateSession,
    service: SessionService = Depends(get_session_service)
):
    result = await service.update_session(session_id, session_data)
    return result

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    result = await service.delete_session(session_id)
    return result