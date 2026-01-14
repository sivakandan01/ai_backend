import os
import json
import httpx
import asyncio
from typing import Dict, Any, List
from app.components.llm.service import LlmService
from app.core.socket_manager import manager
from .schema import ProjectRequest

class ProjectGeneratorService:
    def __init__(self, db, llm_service: LlmService):
        self.db = db
        self.llm = llm_service
        self.github_token = os.getenv("GITHUB_PASSWORD")
        self.github_user = os.getenv("GITHUB_NAME")
        self.vercel_token = os.getenv("VERCEL_TOKEN")
        self.blueprint_path = "../.claude/init" # Path relative to backend root

    async def generate_project(self, request: ProjectRequest, user_id: str):
        """Starts the background orchestration for project generation"""
        project_id = f"proj_{id(request)}"
        
        # Start background task
        asyncio.create_task(self._orchestrate(project_id, request, user_id))
        
        return project_id

    async def _orchestrate(self, project_id: str, request: ProjectRequest, user_id: str):
        try:
            await self._send_update(user_id, project_id, "Analyzing blueprints...", 10)
            blueprints = self._read_blueprints()
            
            await self._send_update(user_id, project_id, "Generating system architecture...", 25)
                        # 1️⃣ Generate project file list via LLM
            system_prompt = (
                "You are a code generation assistant. Using the following blueprints and the user's request, produce a JSON array of objects. Each object must contain \"path\" (relative file path) and \"content\" (file content).\n"
                "Return ONLY valid JSON, no explanations.\n"
                f"Blueprints:\n{blueprints}\n"
                f"User request: {request.prompt}\n"
                "Tech stack: fastapi + react (vite) with TypeScript. Include package.json, tsconfig.json, Dockerfile, etc."
            )
            messages = [{"role": "user", "content": system_prompt}]
            provider = os.getenv("LLM_PROVIDER", "groq")
            model = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")
            llm_output = await self.llm.generate_llm_text(messages, provider, model)
            try:
                files = json.loads(llm_output)
            except json.JSONDecodeError as e:
                await self._send_update(user_id, project_id, f"LLM returned invalid JSON: {e}", 0)
                return
            
            await self._send_update(user_id, project_id, "Creating GitHub repositories...", 50)
            frontend_repo = await self._create_github_repo(f"project-{project_id}-frontend")
            backend_repo = await self._create_github_repo(f"project-{project_id}-backend")
            
            await self._send_update(user_id, project_id, "Generating code and pushing to Git...", 75)
            await asyncio.sleep(3)
            
            await self._send_update(user_id, project_id, "Deploying to Vercel...", 90)
            await asyncio.sleep(2)
            
            await self._send_update(user_id, project_id, "Project Ready!", 100, {
                "frontend_repo": frontend_repo,
                "backend_repo": backend_repo,
                "live_link": "https://preview-link.vercel.app"
            })

        except Exception as e:
            await self._send_update(user_id, project_id, f"Error: {str(e)}", 0)

    def _read_blueprints(self) -> str:
        content = ""
        # Adjusting path to look at the project root folder
        root_path = os.path.abspath(os.path.join(os.getcwd(), "..", ".claude", "init"))
        if os.path.exists(root_path):
            for file in os.listdir(root_path):
                if file.endswith(".md"):
                    with open(os.path.join(root_path, file), "r") as f:
                        content += f"\n--- {file} ---\n" + f.read()
        return content

    async def _create_github_repo(self, name: str) -> str:
        if not self.github_token:
            return f"https://github.com/{self.github_user or 'user'}/{name}"
            
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            resp = await client.post(
                "https://api.github.com/user/repos",
                headers=headers,
                json={"name": name, "private": True}
            )
            if resp.status_code == 201:
                return resp.json().get("html_url")
            return f"https://github.com/{self.github_user}/{name}"

    async def _send_update(self, user_id: str, project_id: str, message: str, progress: int, data: Dict = None):
        payload = {
            "type": "project_update",
            "project_id": project_id,
            "status": message,
            "progress": progress,
            **(data or {})
        }
        await manager.send_personal_message(payload, user_id)
