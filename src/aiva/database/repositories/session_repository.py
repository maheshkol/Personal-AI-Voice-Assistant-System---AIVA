from datetime import datetime
from uuid import uuid4

from aiva.database.collections import Collections


class SessionRepository:

    @staticmethod
    async def create_session(language="en"):

        session_id = f"ses_{uuid4().hex[:8]}"

        document = {
            "session_id": session_id,
            "language": language,
            "started_at": datetime.utcnow(),
            "turn_count": 0
        }

        await Collections.sessions().insert_one(document)

        return session_id

    @staticmethod
    async def increment_turn_count(session_id: str):

        await Collections.sessions().update_one(
            {"session_id": session_id},
            {"$inc": {"turn_count": 1}}
        )