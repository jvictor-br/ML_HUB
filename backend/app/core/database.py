import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URL:
    raise ValueError("A variável MONGO_URL não foi definida no .env")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]