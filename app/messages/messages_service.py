from sqlalchemy import func, or_, desc
from sqlalchemy.orm import joinedload

from app import db
from app.models import Message, User


def create_message(sender_id: int, conversation_id: str, content: str):
    """
    Creates a new messages and saves it
    """
    message = Message(sender_id=sender_id, conversation_id=conversation_id, content=content)
    message.save()
    return message
