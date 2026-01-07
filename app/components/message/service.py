from .schema import CreateMessage
from app.utils.prompt import get_prompt, get_name, get_quick_name
from fastapi import HTTPException, BackgroundTasks
from datetime import datetime
from bson.errors import InvalidId
import logging
from app.helpers.validation import validate_prompt

logger = logging.getLogger(__name__)

class MessageService:

    def __init__(self, db, session_service, llm_service):
        self.db = db
        self.session = session_service
        self.llm = llm_service

    async def save_messages(self, user_data, assistant_data):
        try:
            await self.db.messages.insert_one(user_data)
            await self.db.messages.insert_one(assistant_data)
        except Exception as e:
            logger.error(f"Error saving messages for session {user_data.get('session_id')}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error saving messages")

    async def send_message(self, message: CreateMessage, background_tasks: BackgroundTasks, user):
        session_id = message.session_id
        user_id = user.get("id", "")
        provider = user.get("provider")
        model = user.get("model")

        validate_prompt(message.message, intent="chat")

        messages = []

        try:
            if session_id:
                await self.session.check_session(session_id, user_id)

                messages = await self.db.messages.find({"session_id": session_id}).sort("date", 1).limit(10).to_list(None)
            else:
                session_name = get_quick_name(message.message)

                if session_name is None:
                    name_prompt = get_name(message.message)
                    session_name = await self.llm.generate_llm_text([{"role": "user", "content": name_prompt}], "groq", "llama-3.3-70b-versatile")

                session = await self.session.create_session(user_id, session_name, "message")
                session_id = session["id"]
        except Exception as e:
            raise e

        user_data = {
            "content": message.message,
            "session_id": session_id,
            "role": 'user',
            "date": datetime.utcnow(),
            "is_success": True
        }

        try:
            conversation_messages = []
            for msg in messages:
                conversation_messages.append({"role": msg["role"], "content": msg["content"]})

            conversation_messages.append({"role": "user", "content": message.message})

            response = await self.llm.generate_llm_text(conversation_messages, provider, model)

            assistant_data = {
                "content": response,
                "session_id": session_id, 
                "role": 'assistant',
                "date": datetime.utcnow(),
                "is_success": True
            }

            background_tasks.add_task(self.save_messages, user_data, assistant_data)

            return {
                "content": response,
                "is_success": True,
                "session_id": session_id, 
                "role": "assistant"
            }
        except InvalidId:
            raise HTTPException(status_code=500, detail=f"Invalid Id.")
        except HTTPException as e:
            assistant_data = {
                "content": e.detail,
                "session_id": session_id,  
                "role": 'assistant',
                "date": datetime.utcnow(),
                "is_success": False
            }

            background_tasks.add_task(self.save_messages, user_data, assistant_data)
            raise e
        
    async def get_messages(self, session_id: str, user_id: str):
        try:
            await self.session.check_session(session_id, user_id)

            result = await self.db.messages.aggregate([
                {
                    "$match": { "session_id": session_id }
                },
                {
                    "$project": {
                        "_id": 0,
                        "id": { "$toString": "$_id"},
                        "role": 1,
                        "session_id": 1,
                        "is_success": 1,
                        "content": "$content",
                        "date": 1
                    }
                }
            ]).to_list(length=None)

            return result
        except InvalidId:
            logger.error(f"Invalid ID format in get_messages for session {session_id}")
            raise HTTPException(status_code=500, detail=f"Invalid Id.")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting messages for session {session_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error in Getting Message")