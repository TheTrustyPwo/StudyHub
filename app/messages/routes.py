from flask import flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from app import socketio
from app.models import User, Message
from app.messages import messages_blueprint, messages_service

@login_required
@messages_blueprint.route("/messages")
def messages():
    chats = messages_service.get_chats(current_user.id)
    print(chats)
    return render_template("messages.html", chats=chats)

@login_required
@messages_blueprint.route("/messages/<int:user_id>", methods=["GET", "POST"])
def chat(user_id: int):
    chat_messages = messages_service.get_chat_messages(current_user.id, user_id)
    return render_template("chat.html", messages=chat_messages)

@login_required
@socketio.on('connect', namespace="/messages/socket")
def handle_connect():
    # Join a room based on the user's ID
    user_id = current_user.id
    join_room(user_id)
    print(f"{current_user.username} connected")

@login_required
@socketio.on('disconnect', namespace="/messages/socket")
def handle_disconnect():
    # Leave the room when the user disconnects
    user_id = current_user.id
    leave_room(user_id)
    print(f"{current_user.username} disconnected")

@login_required
@socketio.on('message', namespace="/messages/socket")
def handle_message(payload):
    recipient_id = int(payload['recipient_id'])
    content = payload['content']

    message = messages_service.create_message(current_user.id, recipient_id, content)
    response_data = {
        "id": message.id,
        "sender": current_user.username,
        "sender_id": current_user.id,
        "recipient": User.get_by_id(message.recipient_id).username,
        "recipient_id": message.recipient_id,
        "content": message.content,
        "timestamp": message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }

    print(current_user.username + ": " + content)

    emit('new_message', response_data, room=current_user.id, json=True)
    emit('new_message', response_data, room=recipient_id, json=True)
