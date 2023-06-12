from sqlalchemy import func, or_, desc
from sqlalchemy.orm import joinedload
from typing import List, Union

from app import db
from app.models import Message, User, Conversation, ConversationMember, ReadMessage


def get_user_conversations(user_id: int) -> List[Conversation]:
    """
    Retrieves conversations associated with a specific user.

    :param user_id: The ID of the user.
    :type user_id: int
    :return: A list of conversations associated with the user.
    :rtype: List[Conversation]
    """

    user = User.get_by_id(user_id)
    return [] if user is None else list(user.conversations)


def read_conversation(user_id: int, conversation_id: str):
    # Get the conversation by its ID
    conversation = Conversation.get_by_id(conversation_id)

    if conversation is None:
        # Conversation not found
        return

    # Retrieve all unread messages in the conversation for the user
    unread_messages = db.session.query(Message). \
        filter(Message.conversation_id == conversation_id). \
        filter(~Message.read_users.any(user_id=user_id)). \
        all()

    # Create a list of ReadMessage objects to be inserted
    read_messages = [ReadMessage(message_id=message.id, user_id=user_id) for message in unread_messages]

    # Bulk insert the ReadMessage objects
    db.session.bulk_save_objects(read_messages)

    # Commit the changes to the database
    db.session.commit()

    return read_messages


def private_conversation_exists(user1_id: int, user2_id: int) -> bool:
    """
    Checks if a private conversation exists between 2 users.
    The order of input does not matter.

    :param user1_id: The ID of the first user.
    :type user1_id: int
    :param user2_id: The ID of the second user.
    :type user2_id: int
    :return: True if a private conversation exists, False otherwise.
    :rtype: bool
    """

    conversation = ConversationMember.query.filter_by(user_id=user1_id) \
        .filter(ConversationMember.conversation_id.in_(
            db.session.query(ConversationMember.conversation_id).filter_by(user_id=user2_id)
        )).first()

    return conversation is not None


def create_private_conversation(user1_id: int, user2_id: int) -> Union[Conversation, None]:
    """
    Creates a private one-to-one conversation between 2 users.
    It will not have group conversation attributes such as name, description, and admins.

    :param user1_id: The ID of the first user.
    :type user1_id: int
    :param user2_id: The ID of the second user.
    :type user2_id: int
    :return: The created conversation if successful, None otherwise.
    :rtype: Conversation | None
    """

    if private_conversation_exists(user1_id, user2_id) or user1_id == user2_id:
        return None

    conversation = Conversation(is_group=False)
    conversation.save()

    ConversationMember(user_id=user1_id, conversation_id=conversation.id).save()
    ConversationMember(user_id=user2_id, conversation_id=conversation.id).save()

    return conversation


def create_group_conversation(group_name: str, user_ids: List[int], admin_id: int) -> Conversation:
    """
    Creates a group conversation between multiple users.
    Admin ID should be the ID of the user who created the group.

    :param group_name: The name of the group conversation.
    :type group_name: str
    :param user_ids: A list of user IDs participating in the group conversation.
    :type user_ids: List[int]
    :param admin_id: The ID of the admin user who created the group.
    :type admin_id: int
    :return: The created group conversation.
    :rtype: Conversation
    """

    conversation = Conversation(name=group_name, is_group=True)
    conversation.save()

    for user_id in user_ids:
        member = ConversationMember(user_id=user_id, conversation_id=conversation.id, is_admin=user_id == admin_id)
        member.save()

    return conversation


def check_user_in_conversation(user_id: int, conversation_id: str) -> bool:
    """
    Check if a user is a member of a conversation.

    :param user_id: The ID of the user.
    :type user_id: int
    :param conversation_id: The ID of the conversation.
    :type conversation_id: str
    :return: True if the user is a member of the conversation, False otherwise.
    :rtype: bool
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
