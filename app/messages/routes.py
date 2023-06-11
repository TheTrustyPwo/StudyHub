from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from flask_socketio import emit, join_room, leave_room

from app import socketio
from app.conversations import conversation_services
from app.messages import messages_blueprint, messages_service
from app.models import User, Conversation


@messages_blueprint.route("/messages")
@login_required
def messages():
    return render_template("messages.html")


@socketio.on('connect', namespace="/messages/socket")
@login_required
def handle_connect():
    """
    Join a room based on the user's ID
    """
    user_id = current_user.id
    join_room(user_id)


@socketio.on('disconnect', namespace="/messages/socket")
@login_required
def handle_disconnect():
    """
    Leave the room when the user disconnects
    """
    user_id = current_user.id
    leave_room(user_id)


@socketio.on('message', namespace="/messages/socket")
@login_required
def handle_message(payload):
    conversation_id = payload['conversation_id']
    content = payload['content']

    message = messages_service.create_message(current_user.id, conversation_id, content)
    conversation = Conversation.get_by_id(conversation_id)

    for user in conversation.users:
        emit('new_message', message.serialized, room=user.id, json=True)
