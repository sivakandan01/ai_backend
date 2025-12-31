from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from app.middleware.auth import AuthMiddleware
from contextlib import asynccontextmanager

from app.components.user.routes import router as UserRouter
from app.components.message.routes import router as MessageRouter
from app.components.auth.routes import router as AuthRouter
from app.components.session.routes import router as SessionRouter
from app.components.rag.routes import router as RagRouter
from app.components.image.routes import router as ImageRouter
from app.components.mermaid.routes import router as MermaidRouter

from app.socket.index import socket_app

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://c7ttqdb0-5173.inc1.devtunnels.ms",
        "https://c7ttqdb0-8000.inc1.devtunnels.ms",
        "https://c7ttqdb0-8000.inc1.devtunnels.ms:8000",
        "https://ai-frontend-hiyl.onrender.com"
    ],
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

app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.mount("/socket.io", socket_app)