from flask import jsonify
from flask_login import current_user, login_required

from app.conversations import conversation_services
from app.exceptions import Unauthorized, NotFound
from app.messages import messages_api_blueprint
from app.models import Message


@messages_api_blueprint.route('/<int:message_id>', methods=['GET', ])
@login_required
def get_message(message_id: int):
    message = Message.get_by_id(message_id)
    if not message:
        raise NotFound(message='Message not found')

    if not conversation_services.check_user_in_conversation(current_user.id, message.conversation_id):
        raise Unauthorized(message='You are not in this conversation, and therefore cannot view its messages')

    return jsonify(message.serialized)
