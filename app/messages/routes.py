from flask import render_template, request
from flask_login import current_user, login_required
from flask_socketio import emit, join_room, leave_room

from app import socketio
from app.messages import messages_blueprint, messages_service
from app.models import User


@login_required
@messages_blueprint.route("/messages")
def messages():
    target_id = request.args.get('user')
    if target_id and target_id.isdigit():
        chat_messages = messages_service.get_chat_messages(current_user.id, int(target_id))
        return render_template("chat.html", messages=chat_messages)

    chats = messages_service.get_chats(current_user.id)
    return render_template("messages.html", chats=chats)


@login_required
@socketio.on('connect', namespace="/messages/socket")
def handle_connect():
    """
    Join a room based on the user's ID
    """
    user_id = current_user.id
    join_room(user_id)
    print(f"{current_user.username} connected")


@login_required
@socketio.on('disconnect', namespace="/messages/socket")
def handle_disconnect():
    """
    Leave the room when the user disconnects
    """
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
    print("emitted")
