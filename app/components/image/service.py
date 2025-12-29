from .schema import CreateImage, ImageResponse
from fastapi import HTTPException
from datetime import datetime
import logging
from app.helpers.serializer import serialize_docs
from app.utils.constants import SESSION_TYPE_IMAGE, PROVIDER_POLLINATIONS, STATUS_SUCCESS, STATUS_LOADING

logger = logging.getLogger(__name__)

class ImageService:

    def __init__(self, db, llm_service, session_service):
        self.db = db
        self.llm = llm_service
        self.session = session_service

    async def create_image(self, user, prompt: CreateImage):
        try:
            provider = user.get("image_provider", PROVIDER_POLLINATIONS)
            prompt_text = prompt.prompt
            session_id = prompt.session_id
            user_id = user.get("id")

            if session_id:
                try:
                    await self.session.check_session(session_id, user_id)
                except:
                    session = await self.session.create_session(
                        user_id,
                        "Image Generation",
                        SESSION_TYPE_IMAGE
                    )
                    session_id = session["id"]
            else:
                session = await self.session.create_session(
                    user_id,
                    "Image Generation",
                    SESSION_TYPE_IMAGE
                )
                session_id = session["id"]

            result = await self.llm.generate_llm_image(prompt_text, provider)

            if result.get("status") == STATUS_LOADING:
                return ImageResponse(
                    image_url="",
                    session_id=session_id,
                    status=STATUS_LOADING,
                    message=result.get("message", "Model is loading, try again in 20 seconds")
                )

            image_doc = {
                "prompt": prompt_text,
                "image_url": result.get("image_url", ""),
                "session_id": session_id,
                "user_id": user_id,
                "provider": provider,
                "is_success": True,
                "date": datetime.utcnow()
            }

            await self.db["images"].insert_one(image_doc)

            return ImageResponse(
                image_url=result.get("image_url", ""),
                session_id=session_id,
                status=STATUS_SUCCESS,
                message="Image generated successfully"
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")
        
    async def fetch_images_by_session(self, session_id: str, user_id: str):
        try:
            await self.session.check_session(session_id, user_id)

            result = await self.db.images.find({"session_id": session_id}).to_list(length=None)
            return serialize_docs(result)
        
        except Exception as e:
            raise HTTPException(status_code=404, detail="error fetching images.")