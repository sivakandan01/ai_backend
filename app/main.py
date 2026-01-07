import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.middleware.auth import AuthMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.components.user.routes import router as UserRouter
from app.components.message.routes import router as MessageRouter
from app.components.auth.routes import router as AuthRouter
from app.components.session.routes import router as SessionRouter
from app.components.rag.routes import router as RagRouter
from app.components.image.routes import router as ImageRouter
from app.components.mermaid.routes import router as MermaidRouter

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    from app.helpers.dependencies import get_llm_service
    await get_llm_service().close()

app = FastAPI(
    title="Simple FastAPI App",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
    lifespan=lifespan,
    redirect_slashes=False
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Get allowed origins from environment variable
# Format: comma-separated list of URLs
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

app.include_router(UserRouter)
app.include_router(MessageRouter)
app.include_router(AuthRouter)
app.include_router(SessionRouter)
app.include_router(RagRouter)
app.include_router(ImageRouter)
app.include_router(MermaidRouter)