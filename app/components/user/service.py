from .schema import UserCreate, UserUpdate, UserPatchUpdate
from fastapi import HTTPException
from bson import ObjectId
import logging
from app.helpers.serializer import serialize_docs

# Setup logger
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db):
        self.db = db

    async def fetch_user(self, id: str):
        try:
            user = await self.db.users.find_one({"_id": ObjectId(id)})

            if not user:
                logger.warning(f"User not found with id: {id}")
                raise HTTPException(status_code=404, detail="User not found")

            return {
                "id": str(user["_id"]),
                "user_name": user.get("user_name"),
                "email": user.get("email"),
                "status": user.get("status"),
                "provider": user.get("provider", "ollama"),
                "model": user.get("model", "llama3.2"),
                "image_provider": user.get("image_provider", "pollinations"),
                "theme": user.get("theme", "dark")
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch user {id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")
        
    async def create_user(self, user: UserCreate):
        try:
            user_dict = user.model_dump()

            # Set default values
            user_dict["provider"] = "ollama"
            user_dict["model"] = "llama3.2"
            user_dict["image_provider"] = "pollinations"
            user_dict["theme"] = "dark"

            result = await self.db.users.insert_one(user_dict)
            return await self.fetch_user(str(result.inserted_id))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to create user {user.email}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")
        
    async def update_user(self, user_id: str, user: UserPatchUpdate):
        try:
            user_dict = user.model_dump(exclude_unset=True)

            await self.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_dict})

            return await self.fetch_user(str(user_id))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")
        
    async def fetch_users(self):
        try:
            users = await self.db.users.find().to_list(length=None)

            return serialize_docs(users)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")