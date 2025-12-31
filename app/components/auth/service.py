from .schema import AuthCreate, AuthLogin
from fastapi import HTTPException
from bson import ObjectId
from app.helpers.serializer import serialize_doc
from app.helpers.auth import create_token_response
from app.helpers.validation import hash_password, verify_password
import logging

logger = logging.getLogger(__name__)

class AuthService:

    def __init__(self, db):
        self.db = db

    async def fetch_auth(self, id: str):
        try:
            user = None

            if id:
                user = await self.db.users.find_one({"_id" : ObjectId(id)})

            if not user:
                raise HTTPException(status_code=404, detail="User not found.")

            del user["password"]

            return serialize_doc(user)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching user {id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

    async def login(self, user_data: AuthLogin):
        try:
            user_dict = user_data.model_dump()
            email = user_dict.get("email", "")
            password = user_dict.get("password", "")

            if not email or not password:
                raise HTTPException(
                    status_code=400,
                    detail="Email and password are required"
                )

            existing_user = await self.db.users.find_one({"email" : email})

            if not existing_user:
                raise HTTPException(status_code=401, detail="Invalid email or password.")

            if not verify_password(password, existing_user["password"]):
                raise HTTPException(status_code=401, detail="Invalid email or password.")

            del existing_user["password"]
            serialized_user = serialize_doc(existing_user)

            token = create_token_response(serialized_user)

            return {
                "success": True,
                "messages": "Login successful",
                "user": serialized_user,
                "access_token": token
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during login for {email}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")

    async def register(self, user_data: AuthCreate):
        try:
            user_dict = user_data.model_dump(exclude_none=True)
            email = user_dict.get("email")

            existing_user = await self.db.users.find_one({"email" : email})

            if existing_user:
                raise HTTPException(status_code=409, detail="User already exists with this email.")

            user_dict["password"] = hash_password(user_dict["password"])
            user_dict["provider"] = "ollama"
            user_dict["model"] = "llama3.2"
            user_dict["image_provider"] = "pollinations"
            user_dict["theme"] = "dark"
            user_dict["status"] = "active"
            user_dict["is_edit"] = False

            user = await self.db.users.insert_one(user_dict)
            serialized_user = await self.fetch_auth(str(user.inserted_id))

            token = create_token_response(serialized_user)

            return {
                "success": True,
                "messages": "Registration successful",
                "user": serialized_user,
                "access_token": token
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during registration for {email}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error during registration: {str(e)}")