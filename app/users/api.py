from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required

from app.models import User
from app.exceptions import NotFound
from app.users import user_api_blueprint, user_service


@user_api_blueprint.route("/current")
def get_current_user():
    """
    Retrieve current user data, usually used by AJAX requests
    """
    return jsonify(current_user.serialized)

@user_api_blueprint.route('/<int:user_id>')
def get_user_by_id(user_id: int):
    user = User.get_by_id(user_id)
    if not user:
        raise NotFound(message='User not found')
    return jsonify(user.serialized)

@user_api_blueprint.route('/<string:username>')
def get_user_by_username(username: str):
    user = User.get_by_username(username)
    if not user:
        raise NotFound(message='User not found')
    return jsonify(user.serialized)
