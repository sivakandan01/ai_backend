from fastapi import APIRouter, Depends, Request
from app.helpers.auth import check_for_auth
from app.helpers.dependencies import get_image_service
from .schema import CreateImage

router = APIRouter(prefix="/image", tags=["image"], dependencies=[Depends(check_for_auth)])

@router.post("/generate")
async def create_image(request: Request, prompt: CreateImage, service = Depends(get_image_service)):
    user = request.state.user
    result = await service.create_image(user, prompt)
    return result

@router.get("/{session_id}")
async def get_image(session_id: str, request: Request, service = Depends(get_image_service)):
    user = request.state.user
    result = await service.fetch_images_by_session(session_id, user.get("id", ""))
    return result