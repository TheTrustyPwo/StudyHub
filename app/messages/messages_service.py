from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app import db
from app.models import Message, User


def create_message(sender_id: int, recipient_id: int, content: str):
    """
    Creates a new messages and saves it
    """
    message = Message(sender_id=sender_id, recipient_id=recipient_id, content=content)
    message.save()
    return message


def get_chats(sender_id: int):
    """
    Returns the all user ids that the sender has chatted with, sorted by last message time
    """
    subquery = db.session.query(
        Message.recipient_id,
        func.max(Message.timestamp).label('last_timestamp')
    ).filter(Message.sender_id == sender_id).group_by(Message.recipient_id).subquery()

    query = db.session.query(
        User.id,
        User.username,
        Message.content,
        Message.timestamp
    ).join(
        subquery, User.id == subquery.c.recipient_id
    ).join(
        Message, (Message.sender_id == sender_id) & (Message.recipient_id == subquery.c.recipient_id) & (
                    Message.timestamp == subquery.c.last_timestamp)
    ).order_by(subquery.c.last_timestamp.desc()).all()

    return query


def get_chat_messages(user1_id: int, user2_id: int):
    messages = Message.query.join(User, Message.sender_id == User.id).filter(
        ((Message.sender_id == user1_id) & (Message.recipient_id == user2_id)) |
        ((Message.sender_id == user2_id) & (Message.recipient_id == user1_id))
    ).options(joinedload(Message.sender), joinedload(Message.recipient)).order_by(Message.timestamp.asc())

    return messages
