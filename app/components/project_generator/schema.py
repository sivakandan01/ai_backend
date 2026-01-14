from pydantic import BaseModel
from typing import List, Optional

class ProjectRequest(BaseModel):
    prompt: str
    tech_stack: Optional[str] = "fastapi-react"

class ProjectStatusResponse(BaseModel):
    project_id: str
    status: str
    frontend_repo: Optional[str] = None
    backend_repo: Optional[str] = None
    live_link: Optional[str] = None
    progress: int = 0
    logs: List[str] = []

class ProjectResponse(BaseModel):
    project_id: str
    message: str
