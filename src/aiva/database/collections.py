from aiva.database.mongo_client import MongoDBClient


class Collections:

    @staticmethod
    def messages():
        return MongoDBClient.get_db()["messages"]

    @staticmethod
    def sessions():
        return MongoDBClient.get_db()["sessions"]

    @staticmethod
    def api_logs():
        return MongoDBClient.get_db()["api_logs"]