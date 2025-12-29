from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from app.helpers.auth import get_user_from_token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = None

        authorization = request.headers.get("Authorization")
        if authorization:
            token = authorization.split()[-1]

        if not token:
            token = request.cookies.get("access_token")

        if token:
            try:
                user = await get_user_from_token(token)
                request.state.is_authenticated = True
                request.state.user = user
            except:
                request.state.is_authenticated = False
                request.state.user = None
        else:
            request.state.is_authenticated = False
            request.state.user = None

        response = await call_next(request)

        return response