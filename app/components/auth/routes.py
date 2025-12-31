from fastapi import APIRouter, Depends, Response
from .schema import AuthCreate, AuthLogin, AuthResponse
from .service import AuthService
from app.helpers.auth import check_for_auth
from app.helpers.dependencies import get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(
    user_data: AuthLogin,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):
    result = await service.login(user_data)

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        max_age=86400,
        samesite="lax"
    )

    return result

@router.post("/register")
async def register(
    user_data: AuthCreate,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):
    result = await service.register(user_data)

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        max_age=86400,
        samesite="lax"
    )

    return result

@router.get("/{user_id}", response_model=AuthResponse)
async def fetch_user(
    user_id: str,
    service: AuthService = Depends(get_auth_service)
):
    result = await service.fetch_auth(user_id)
    return result