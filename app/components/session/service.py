from fastapi import HTTPException
from bson import ObjectId
from app.helpers.serializer import serialize_doc, serialize_docs
from bson.errors import InvalidId
from .schema import UpdateSession
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class SessionService:

    def __init__(self, db):
        self.db = db

    async def fetch_sessions(self, user, type: str):
        try:
            result = await self.db.sessions.find({"user_id": user.get("id", ""), "type": type}).sort("date", 1).to_list(length=None)
            return serialize_docs(result)
        except Exception as e:
            logger.error(f"Error fetching sessions for user {user.get('id')}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error Fetching Sessions.")

    async def fetch_session_by_id(self, session_id: str):
        try:
            session = await self.db.sessions.find_one({"_id": ObjectId(session_id)})
            if not session:
                raise HTTPException(status_code=404, detail="Session Not Found.")
            return serialize_doc(session)
        except InvalidId:
            logger.error(f"Invalid session ID format: {session_id}")
            raise HTTPException(status_code=500, detail=f"Invalid Session Id.")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching session {session_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error Fetching Sessions.")

    async def create_session(self, user_id, session_name: str, type: str):
        try:
            session = await self.db.sessions.insert_one({
                "user_id": user_id,
                "session_name": session_name,
                "date": datetime.utcnow(),
                "type": type
            })
            result = await self.fetch_session_by_id(str(session.inserted_id))
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating session for user {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error Creating Session: {str(e)}")

    async def check_session(self, session_id, user_id):
        try:
            session = await self.db.sessions.find_one({"_id": ObjectId(session_id)})

            if not session:
                raise HTTPException(status_code=404, detail="Session Not Found.")

            if (session and session["user_id"]) != user_id:
                raise HTTPException(status_code=401, detail="User Doesn't have permission to see this Session.")
        except InvalidId:
            logger.error(f"Invalid session ID format: {session_id}")
            raise HTTPException(status_code=500, detail=f"Invalid Session Id.")
        except HTTPException:
            raise

    async def update_session(self, session_id: str, session_data: UpdateSession):
        try:
            session = await self.db.sessions.update_one(
                {"_id": ObjectId(session_id)},
                { "$set": session_data.model_dump() }
            )
            if session.matched_count == 0:
                raise HTTPException(status_code=404, detail="Session Not Found.")
            return await self.fetch_session_by_id(session_id)
        except InvalidId:
            logger.error(f"Invalid session ID format: {session_id}")
            raise HTTPException(status_code=500, detail=f"Invalid Session Id.")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error Updating Session: {str(e)}")

    async def delete_session(self, session_id: str):
        try:
            session = await self.db.sessions.delete_one({"_id": ObjectId(session_id)})
            if session.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Session Not Found.")
            return { "message": "Session Deleted SuccessFully." }
        except InvalidId:
            logger.error(f"Invalid session ID format: {session_id}")
            raise HTTPException(status_code=500, detail=f"Invalid Session Id.")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error Deleting Session: {str(e)}")
            
