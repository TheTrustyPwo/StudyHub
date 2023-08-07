from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required

from app.conversations import conversations_blueprint, conversation_services
from app.models import User


@conversations_blueprint.route("/conversations/data")
@login_required
def conversations_data():
    convs = conversation_services.get_user_conversations(current_user.id)
    return jsonify({'conversations': [conv.serialized for conv in convs]})
