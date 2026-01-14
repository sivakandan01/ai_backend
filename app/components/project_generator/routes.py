from fastapi import APIRouter, Depends, Request
from app.helpers.auth import check_for_auth
from .schema import ProjectRequest, ProjectResponse
from app.helpers.dependencies import get_project_generator_service

router = APIRouter(prefix="/project-generator", tags=["project-generator"])

@router.post("/generate", response_model=ProjectResponse)
async def generate_project(
    request: ProjectRequest,
    req: Request,
    service = Depends(get_project_generator_service),
    _ = Depends(check_for_auth)
):
    user = req.state.user
    project_id = await service.generate_project(request, user.get("id"))
    return {
        "project_id": project_id,
        "message": "Project generation started in background."
    }
