from typing import Dict
from app.models.conversation import Conversation
from app.models.message import Message
from app.extensions import db

class OllamaMapper:
    @staticmethod
    def chat() -> str:
        # # Save conversation to database
        # model_id = db.fetch_one("SELECT id FROM models WHERE name = %s", (conversation.model_name,))['id']
        # insert_query = "INSERT INTO conversations (model_id, user_message, assistant_message) VALUES (%s, %s, %s)"
        # db.execute_query(insert_query, (model_id, conversation.messages[-1]['content'], response.response))
        pass