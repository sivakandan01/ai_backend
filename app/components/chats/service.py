from .schema import CreateChats, UpdateChats
from bson import ObjectId
from app.helpers.serializer import serialize_doc, serialize_docs
from datetime import datetime

class ChatService:
    def __init__(self, db):
        self.db = db

    async def fetch_chat_id(self, chat_id: str):
        try:
            result = await self.db.chats.find_one({"_id": ObjectId(chat_id)})
            return serialize_doc(result)
        except:
            return None

    async def create_chat(self, chats: CreateChats, user):
        try:
            user_id = user.get("id")
            count = await self.db.chats.count_documents({
                "$or": [
                    {"sender_id": user_id, "receiver_id": chats.receiver_id},
                    {"sender_id": chats.receiver_id, "receiver_id": user_id}
                ]
            })
            is_new = (count == 0)

            chat_data = chats.model_dump()
            chat_data["sender_id"] = user_id
            chat_data["created_at"] = datetime.now()
            chat_data["status"] = "sent"
            chat_data["is_read"] = False
            
            result = await self.db.chats.insert_one(chat_data)
            message = await self.fetch_chat_id(str(result.inserted_id))
            return message, is_new
        except Exception as e:
            print(f"Error in create_chat: {e}")
            return None, False

    async def fetch_chat(self, receiver_id: str, user):
        try:
            user_id = user.get("id")
            query = {
                "$or": [
                    {"sender_id": user_id, "receiver_id": receiver_id},
                    {"sender_id": receiver_id, "receiver_id": user_id}
                ]
            }
            results = await self.db.chats.find(query).sort("created_at", 1).to_list(length=None)
            return serialize_docs(results)
        except Exception as e:
            print(f"Error in fetch_chat: {e}")
            return []

    async def update_chat(self, chat_id: str, chats: UpdateChats, user):
        try:
            update_data = chats.model_dump(exclude_unset=True)
            if not update_data:
                return await self.fetch_chat_id(chat_id)
                
            await self.db.chats.update_one(
                {"_id": ObjectId(chat_id)},
                {"$set": update_data}
            )
            return await self.fetch_chat_id(chat_id)
        except Exception as e:
            print(f"Error in update_chat: {e}")
            return None

    async def fetch_conversations(self, user_id: str):
        try:
            pipeline = [
                {
                    "$match": { 
                        "$or": [
                            {"sender_id": user_id}, {"receiver_id": user_id}
                        ]
                    }
                },
                {"$sort": {"created_at": -1}},
                { "$group": {
                        "_id": {
                            "$cond": [
                                { "$eq": ["$sender_id", user_id] },
                                "$receiver_id",
                                "$sender_id"
                            ]
                        },
                        "last_message": {"$first": "$content"},
                        "last_message_date": {"$first": "$created_at"}
                    }
                },
                {"$lookup": {
                    "from": "users",
                    "let": {"other_user_id": "$_id"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$other_user_id"]}}}
                    ],
                    "as": "user_info"
                }},
                {"$unwind": "$user_info"},
                {
                    "$project": {
                        "id": { "$toString": "$_id" },
                        "user_name": "$user_info.user_name",
                        "email": "$user_info.email",
                        "last_message": 1,
                        "last_message_date": 1
                    }
                }
            ]

            results = await self.db.chats.aggregate(pipeline).to_list(length=None)     
            return results
        except Exception as e:
            print(f"Error in fetch_conversations: {e}")
            return []