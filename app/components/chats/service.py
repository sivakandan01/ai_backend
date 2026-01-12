from .schema import CreateChats, UpdateChats

class ChatService:
    def __init__(self, db):
        self.db = db

    async def create_chat(self, chats: CreateChats, user):
        pass

    async def fetch_chat(self, receiver_id: str, user):
        pass

    async def update_chat(self, chats: UpdateChats, user):
        pass