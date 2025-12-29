from fastapi import APIRouter, Depends, Request
from app.helpers.auth import check_for_auth
from app.helpers.dependencies import get_mermaid_service
from .schema import CreateMermaid

router = APIRouter(prefix="/mermaid", tags=["mermaid"], dependencies=[Depends(check_for_auth)])

@router.post("/generate")
async def create_mermaid(request: Request, prompt: CreateMermaid, service = Depends(get_mermaid_service)):
    user = request.state.user
    result = await service.create_mermaid(user, prompt)
    return result

@router.get("/{session_id}")
async def fetch_mermaids_session(session_id: str, service = Depends(get_mermaid_service)):
    result = await service.fetch_mermaids_by_session(session_id)
    return result