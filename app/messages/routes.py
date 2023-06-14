from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from flask_socketio import emit, join_room, leave_room

from app import socketio
from app.conversations import conversation_services
from app.exceptions import APIException, Unauthorized, BadRequest
from app.messages import messages_blueprint, messages_service
from app.models import Conversation, Message


@messages_blueprint.route("/messages")
@login_required
def messages():
    """
    Render the messages template.

    :return: Rendered messages template.
    :rtype: flask.Response
    """
    return render_template("messages.html")


@socketio.on('connect', namespace="/messages/socket")
@login_required
def handle_connect():
    """
    Handle the user connection event.

    Join a room based on the user's ID.
    """
    user_id = current_user.id
    join_room(user_id)


@socketio.on('disconnect', namespace="/messages/socket")
@login_required
def handle_disconnect():
    """
    Handle the user disconnection event.

    Leave the room when the user disconnects.
    """
    user_id = current_user.id
    leave_room(user_id)


@socketio.on('message', namespace="/messages/socket")
@login_required
def handle_message(payload):
    """
    Handle the message event.

    Create a new message and emit it to the appropriate users in the conversation.

    :param payload: The message payload containing conversation ID and content.
    :type payload: dict
    """
    conversation_id = payload['conversation_id']
    content = payload['content']

    if not conversation_id:
        raise BadRequest(message='conversation_id is not specified in payload')

    if not content:
        raise BadRequest(message='content is not specified in payload')

    message = messages_service.create_message(current_user.id, conversation_id, content)
    conversation = Conversation.get_by_id(conversation_id)

    for user in conversation.users:
        emit('new_message', message.serialized, room=user.id, json=True)


@socketio.on('read_message', namespace='/messages/socket')
@login_required
def handle_read_message(payload):
    """
    Handle the read message event.

    Mark a message as read by the current user and emit the bluetick event
    to the conversation users if all members have read the message.

    :param payload: The read message payload containing the message ID.
    :type payload: dict
    """
    message_id = payload['message_id']

    if not message_id:
        raise BadRequest(message='message_id is not specified in payload')

    message = Message.get_by_id(message_id)
    read_message_data = messages_service.read_message(message_id, current_user.id)

    if not read_message_data.message.read_by_all:
        return

    for user in message.conversation.users:
        emit('bluetick', [read_message_data.message.id], room=user.id, json=True)


@socketio.on('read_conversation', namespace='/messages/socket')
@login_required
def handle_read_conversation(payload):
    """
    Handle the read conversation event.

    Mark all messages in a conversation as read by the current user and
    emit the bluetick event to the conversation users if all members have read the message.

    :param payload: The read conversation payload containing the conversation ID.
    :type payload: dict
    """
    conversation_id = payload['conversation_id']

    if not conversation_id:
        raise BadRequest(message='conversation_id is not specified in payload')

    conversation = Conversation.get_by_id(conversation_id)
    if current_user not in conversation.users:
        raise Unauthorized(message='User cannot read conversation it is not part of')

    read_messages_data = conversation_services.read_conversation(current_user.id, conversation_id)
    emit_data = [data.message.id for data in read_messages_data if data.message.read_by_all]

    if not emit_data:
        return

    for user in conversation.users:
        emit('bluetick', emit_data, room=user.id, json=True)


@socketio.on('edit_message', namespace='/messages/socket')
@login_required
def handle_edit_message(payload: dict):
    """
    Handle the edit message event.

    Edit a message content if the user is the message sender,
    and emit the edited message to the conversation users.

    :param payload: The edit message payload containing the message ID and new content.
    :type payload: dict
    """
    message_id = payload['message_id']
    new_content = payload['new_content']

    if not message_id:
        raise BadRequest(message='message_id is not specified in payload')

    if not new_content:
        raise BadRequest(message='new_content is not specified in payload')

    message = Message.get_by_id(message_id)
    if message.sender_id != current_user.id:
        raise Unauthorized(message='User cannot edit messages of other users')

    message.content = new_content
    message.save()

    for user in message.conversation.users:
        emit('edit', {'id': message.id, 'content': message.content}, room=user.id, json=True)


@socketio.on('delete_message', namespace='/messages/socket')
@login_required
def handle_delete_message(payload: dict):
    """
    Handle the delete message event.

    Delete a message if the user is the message sender,
    and emit the deleted message ID to the conversation users.

    :param payload: The delete message payload containing the message ID.
    :type payload: dict
    """
    message_id = payload['message_id']
    if not message_id:
        raise BadRequest(message='message_id is not specified in payload')

    message = Message.get_by_id(message_id)
    if message.sender_id != current_user.id:
        raise Unauthorized(message='User cannot delete messages of other users')

    message.delete()

    for user in message.conversation.users:
        emit('delete', {'id': message_id}, room=user.id, json=True)
