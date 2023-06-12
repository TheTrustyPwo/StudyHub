from sqlalchemy import func, or_, desc
from sqlalchemy.orm import joinedload

from app import db
from app.models import Message, User, ReadMessage


def create_message(sender_id: int, conversation_id: str, content: str) -> Message:
    """
    Create a new message and save it.

    :param sender_id: The ID of the message sender.
    :type sender_id: int
    :param conversation_id: The ID of the conversation the message belongs to.
    :type conversation_id: str
    :param content: The content of the message.
    :type content: str
    :return: The created message object.
    :rtype: Message
    """
    message = Message(sender_id=sender_id, conversation_id=conversation_id, content=content)
    message.save()
    return message


def read_message(message_id: int, user_id: int) -> ReadMessage:
    """
    Read a message for a specific user.

    If the message has already been read by the user, return the existing ReadMessage object.
    If the message has not been read by the user, create a new ReadMessage object and save it.

    :param message_id: The ID of the message to read.
    :type message_id: int
    :param user_id: The ID of the user who reads the message.
    :type user_id: int
    :return: The ReadMessage object representing the message read by the user.
    :rtype: ReadMessage
    """
    read_message_data = ReadMessage.query.filter_by(message_id=message_id, user_id=user_id).first()
    if read_message_data is not None:
        return read_message_data

    read_message_data = ReadMessage(message_id=message_id, user_id=user_id)
    read_message_data.save()
    return read_message_data
