from .schema import CreateMermaid, MermaidResponse
from fastapi import HTTPException
from datetime import datetime
import logging
from app.utils.constants import SESSION_TYPE_MERMAID, DEFAULT_PROVIDER, DEFAULT_MODEL
from app.helpers.serializer import serialize_docs

logger = logging.getLogger(__name__)

class MermaidService:

    def __init__(self, db, llm_service, session_service):
        self.db = db
        self.llm = llm_service
        self.session = session_service

    async def create_mermaid(self, user, prompt: CreateMermaid):
        try:
            provider = user.get("provider", DEFAULT_PROVIDER)
            model = user.get("model", DEFAULT_MODEL)
            prompt_text = prompt.prompt
            session_id = prompt.session_id
            user_id = user.get("id")

            if session_id:
                try:
                    await self.session.check_session(session_id, user_id)
                except:
                    session = await self.session.create_session(
                        user_id,
                        "Mermaid Diagram",
                        SESSION_TYPE_MERMAID
                    )
                    session_id = session["id"]
            else:
                session = await self.session.create_session(
                    user_id,
                    "Mermaid Diagram",
                    SESSION_TYPE_MERMAID
                )
                session_id = session["id"]

            result = await self.llm.generate_llm_flowchart(prompt_text, provider, model)

            mermaid_doc = {
                "prompt": prompt_text,
                "mermaid_code": result.get("mermaid_code", ""),
                "session_id": session_id,
                "user_id": user_id,
                "provider": provider,
                "model": model,
                "is_success": True,
                "date": datetime.utcnow()
            }

            db_result = await self.db["mermaids"].insert_one(mermaid_doc)

            return MermaidResponse(
                mermaid_code=result.get("mermaid_code", ""),
                session_id=session_id,
                diagram_id=str(db_result.inserted_id)
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating diagram: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating diagram: {str(e)}")
        
    async def fetch_mermaids_by_session(self, session_id):
        try:
            result = await self.db.mermaids.find({"session_id": session_id}).to_list(length=None)
            return serialize_docs(result)
        except Exception as e:
            raise HTTPException(status_code=404, detail="error fetching images.")