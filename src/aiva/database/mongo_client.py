from motor.motor_asyncio import AsyncIOMotorClient
import os


class MongoDBClient:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        """
        Create MongoDB connection.
        """
        if cls.client is None:
            mongo_uri = os.getenv("MONGODB_URI")
            db_name = os.getenv("MONGODB_DB_NAME", "aiva_db")

            cls.client = AsyncIOMotorClient(mongo_uri)
            cls.db = cls.client[db_name]

            print("✅ MongoDB connected")

    @classmethod
    def get_db(cls):
        return cls.db