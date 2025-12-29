from app.core.database import db
from app.components.session.service import SessionService
from app.components.llm.service import LlmService
from app.components.message.service import MessageService
from app.components.user.service import UserService
from app.components.auth.service import AuthService
from app.components.rag.service import RagService
from app.components.image.service import ImageService
from app.components.mermaid.service import MermaidService

class ServiceContainer:
    def __init__(self):
        self.llm = LlmService(db)
        self.session = SessionService(db)
        self.user = UserService(db)
        self.auth = AuthService(db)

        self.message = MessageService(db, self.session, self.llm)
        self.rag = RagService(db, self.llm)
        self.image = ImageService(db, self.llm, self.session)
        self.mermaid = MermaidService(db, self.llm, self.session)

_services = None

def get_services() -> ServiceContainer:
    global _services
    if _services is None:
        _services = ServiceContainer()
    return _services

def get_session_service() -> SessionService:
    return get_services().session

def get_message_service() -> MessageService:
    return get_services().message

def get_user_service() -> UserService:
    return get_services().user

def get_auth_service() -> AuthService:
    return get_services().auth

def get_llm_service() -> LlmService:
    return get_services().llm

def get_rag_service() -> RagService:
    return get_services().rag

def get_image_service() -> ImageService:
    return get_services().image

def get_mermaid_service() -> MermaidService:
    return get_services().mermaid