import motor.motor_asyncio
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL=os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME=os.getenv("DATABASE_NAME", "fastapi_app")

client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client[DATABASE_NAME]