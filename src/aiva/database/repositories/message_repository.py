from datetime import datetime
from aiva.database.collections import Collections


class MessageRepository:

    @staticmethod
    async def save_message(
        session_id: str,
        turn_index: int,
        user_input: str,
        response: str,
        intent: str,
        tool_used: str,
        latency_ms: int,
        language: str = "en"
    ):

        document = {
            "session_id": session_id,
            "turn_index": turn_index,
            "user_input": user_input,
            "response": response,
            "intent": intent,
            "tool_used": tool_used,
            "latency_ms": latency_ms,
            "language": language,
            "timestamp": datetime.utcnow()
        }

        await Collections.messages().insert_one(document)

    @staticmethod
    async def get_session_messages(session_id: str):

        cursor = Collections.messages().find(
            {"session_id": session_id}
        ).sort("timestamp", 1)

        return await cursor.to_list(length=100)