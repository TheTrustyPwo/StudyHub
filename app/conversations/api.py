import datetime

from flask import request, jsonify
from flask_login import current_user, login_required

from app.conversations import conversations_api_blueprint, conversation_services
from app.exceptions import BadRequest, Unauthorized, NotFound, Conflict
from app.models import User, Conversation


@conversations_api_blueprint.route('/data/all')
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
    return jsonify({'conversations': [conv.serialized for conv in convs]})


@conversations_api_blueprint.route('/data/<string:conversation_id>')
@login_required
def get_conversation(conversation_id: str):
    conversation = Conversation.get_by_id(conversation_id)
    if conversation is None:
        abort(404, 'That conversation does not exist!')

    if not conversation_services.check_user_in_conversation(current_user.id, conversation_id):
        abort(401, 'You are not in this conversation, and therefore cannot view its data')

    return jsonify(conversation.serialized)


@conversations_api_blueprint.route('/history/<string:conversation_id>')
@login_required
def get_conversation_history(conversation_id: str):
    conversation = Conversation.get_by_id(conversation_id)
    if conversation is None:
        abort(404, 'That conversation does not exist!')

    if not conversation_services.check_user_in_conversation(current_user.id, conversation_id):
        abort(401, 'You are not in this conversation, and therefore cannot view its data')

    return jsonify({'messages': [message.serialized for message in conversation.messages]})
