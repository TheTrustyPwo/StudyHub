import datetime

from flask import request, jsonify
from flask_login import current_user, login_required

from app.conversations import conversations_api_blueprint, conversation_services
from app.exceptions import BadRequest, Unauthorized, NotFound, Conflict
from app.models import User, Conversation


@conversations_api_blueprint.route('/all')
@login_required
def get_all_conversations():
    """
    Get all conversations for the current user.

    :return: A JSON response containing the serialized conversations.
    :rtype: flask.Response
    """

    def last_update(conv: Conversation) -> datetime.datetime:
        """
        Inner function to determine the time of the latest update that occurred in a conversation
        by taking the max of the creation time and time of last message; Used to sort conversations

        :param conv: Conversation to evaluate
        :type conv: Conversation
        :return: Time of the last update
        :rtype: datetime.datetime
        """
        messages = list(conv.messages)
        if messages:
            return max(messages[-1].timestamp, conv.date_created)
        return conv.date_created

    convs = conversation_services.get_user_conversations(current_user.id)
    convs.sort(key=lambda conv: last_update(conv), reverse=True)
    return jsonify([conv.serialized for conv in convs])


@conversations_api_blueprint.route('/<string:conversation_id>', methods=['GET', ])
@login_required
def get_conversation(conversation_id: str):
    """
    Get a specific conversation by its ID.

    :param conversation_id: The ID of the conversation.
    :type conversation_id: str
    :return: A JSON response containing the serialized conversation.
    :rtype: flask.Response
    :raises 404: If the conversation with the given ID is not found.
    :raises 401: If the current user is not a participant in the conversation.
    """

    conversation = Conversation.get_by_id(conversation_id)
    if not conversation:
        raise NotFound(message='Conversation not found')

    if not conversation_services.check_user_in_conversation(current_user.id, conversation_id):
        raise Unauthorized(message='You are not in this conversation, and therefore cannot view its data')

    return jsonify(conversation.serialized)


@conversations_api_blueprint.route('/history/<string:conversation_id>')
@login_required
def get_conversation_history(conversation_id: str):
    """
    Get the history of a specific conversation by its ID.

    :param conversation_id: The ID of the conversation.
    :type conversation_id: str
    :return: A JSON response containing the serialized messages of the conversation.
    :rtype: flask.Response
    :raises 404: If the conversation with the given ID is not found.
    :raises 401: If the current user is not a participant in the conversation.
    """

    conversation = Conversation.get_by_id(conversation_id)
    if not conversation:
        raise NotFound(message='Conversation not found')

    if not conversation_services.check_user_in_conversation(current_user.id, conversation_id):
        raise Unauthorized(message='You are not in this conversation, and therefore cannot view its data')

    onlyGetMessageIds = request.args.get('onlyGetId', default='false').lower() == 'true'
    if onlyGetMessageIds:
        return jsonify([message.id for message in conversation.messages])
    return jsonify([message.serialized_min for message in conversation.messages])


@conversations_api_blueprint.route('/new/private', methods=['POST', ])
@login_required
def create_private_conversation():
    """
    Create a private conversation between the current user and a target user.

    :return: A JSON response containing the serialized conversation.
    :rtype: flask.Response
    :raises 400: If the request does not specify the user to create a private conversation with,
                 or the specified user is the current user
    :raises 409: If the current user attempts to create a conversation with themselves
                 or if a conversation already exists between the users.
    """
    target_id = request.json['target']
    if not target_id:
        raise BadRequest(message='Target user ID was not specified')

    if not User.get_by_id(target_id):
        raise BadRequest(message='User ID is invalid')

    if current_user.id == target_id:
        raise BadRequest(message='Target user ID cannot be current user ID')

    conversation = conversation_services.create_private_conversation(current_user.id, target_id)

    if not conversation:
        raise Conflict(message='A conversation already exists between the users')

    return jsonify(conversation.serialized)


@conversations_api_blueprint.route('/new/group', methods=['POST', ])
@login_required
def create_group_conversation():
    """
    Create a group conversation with multiple users.

    :return: A JSON response containing the serialized conversation.
    :rtype: flask.Response
    :raises 400: If the group name or the group members were not specified
                 or the provided list of group members contains invalid users
    """

    group_name = request.json['name']
    if not group_name:
        raise BadRequest(message='Group name was not specified')

    user_ids = request.json['users']
    if not user_ids:
        raise BadRequest(message='User IDs were not specified')

    for user_id in user_ids:
        if not User.get_by_id(user_id):
            raise BadRequest(message='One of more of the provided user IDs was invalid')

    if current_user.id not in user_ids:
        user_ids.append(current_user.id)

    conversation = conversation_services.create_group_conversation(group_name, user_ids, current_user.id)
    return jsonify(conversation.serialized)
