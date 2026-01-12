from fastapi import APIRouter, Depends, Request, Query
from typing import List
from .schema import User, UserCreate, UserUpdate, UserPatchUpdate, UserFilterResponse
from .service import UserService
from app.helpers.auth import check_for_auth
from app.helpers.dependencies import get_user_service
from typing import Optional

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(check_for_auth)])

@router.post("/", response_model=User)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    result = await service.create_user(user)
    return result


@router.get("/", response_model=List[UserFilterResponse])
async def get_all_users(search: Optional[str] = Query(None), service: UserService = Depends(get_user_service)):
    search = search.strip() if search else None
    result = await service.fetch_users(search)
    return result


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    result = await service.fetch_user(user_id)
    return result


@router.patch("/", response_model=User)
async def update_user(user_update: UserPatchUpdate, request: Request, service: UserService = Depends(get_user_service)):
    user = request.state.user
    result = await service.update_user(user.get("id"), user_update)
    return result


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    # TODO: Add service logic here
    pass