from sqlalchemy import func, or_, desc
from sqlalchemy.orm import joinedload
from typing import Tuple

from app import db
from app.models import Message, User, Conversation, ConversationMember


def get_user_conversations(user_id: int):
    """
    Retrieves conversations associated with a specific user
    """
    user = User.get_by_id(user_id)
    return [] if user is None else user.conversations


def private_conversation_exists(user1_id: int, user2_id: int) -> bool:
    """
    Checks if a private conversation exists between 2 users
    The other of input does not matter
    """
    conversation = ConversationMember.query.filter_by(user_id=user1_id) \
        .filter(ConversationMember.conversation_id.in_(
            db.session.query(ConversationMember.conversation_id).filter_by(user_id=user2_id)
        )).first()

    return conversation is not None


def create_private_conversation(user1_id: int, user2_id: int) -> Conversation | None:
    """
    Creates a private one to one conversation between 2 users
    It will not have group conversation attributes such as name, description and admins
    """
    if private_conversation_exists(user1_id, user2_id) or user1_id == user2_id:
        return None

    conversation = Conversation(is_group=False)
    conversation.save()

    ConversationMember(user_id=user1_id, conversation_id=conversation.id).save()
    ConversationMember(user_id=user2_id, conversation_id=conversation.id).save()

    return conversation


def create_group_conversation(group_name: str, user_ids: Tuple[int], admin_id: int):
    """
    Creates a group conversation between multiple users
    Admin ID should be the id of the user who created the group
    """
    conversation = Conversation(name=group_name, is_group=False)
    conversation.save()

    for user_id in user_ids:
        member = ConversationMember(user_id=user_id, conversation_id=conversation.id, is_admin=user_id == admin_id)
        member.save()

    return conversation


def check_user_in_conversation(user_id, conversation_id):
    """
    Check if a user is a member of a conversation
    """
    # Retrieve the User and Conversation objects
    user = User.get_by_id(user_id)
    conversation = Conversation.get_by_id(conversation_id)

    if user is None or conversation is None:
        # User or Conversation not found
        return False

    # Check if the user is a member of the conversation
    member = ConversationMember.query.filter_by(user_id=user_id, conversation_id=conversation_id).first()
    return member is not None
