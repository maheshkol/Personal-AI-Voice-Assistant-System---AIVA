import uuid
from datetime import datetime


class SessionManager:

    @staticmethod
    def generate_session_id():

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        unique_id = str(uuid.uuid4())[:8]

        return f"session_{timestamp}_{unique_id}"