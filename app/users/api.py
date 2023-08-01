import flask
from flask import jsonify
from flask_login import current_user
from typing import List

from app.exceptions import NotFound
from app.models import User
from app.users import user_api_blueprint


@user_api_blueprint.route("/current")
def get_current_user() -> flask.Response:
    """
    Retrieve current user data, usually used by AJAX requests.

    :return: JSON representation of the current user data.
    """
    return jsonify(current_user.serialized)


@user_api_blueprint.route('/<int:user_id>')
def get_user_by_id(user_id: int) -> flask.Response:
    """
    Get user data by user ID.

    :param user_id: The ID of the user to retrieve.
    :return: JSON representation of the user data.
    """
    user = User.get_by_id(user_id)
    if not user:
        raise NotFound(message='User not found')
    return jsonify(user.serialized)


@user_api_blueprint.route('/<string:username>')
def get_user_by_username(username: str) -> flask.Response:
    """
    Get user data by username.

    :param username: The username of the user to retrieve.
    :return: JSON representation of the user data.
    """
    user = User.get_by_username(username)
    if not user:
        raise NotFound(message='User not found')
    return jsonify(user.serialized)


@user_api_blueprint.route('/search/<string:query>')
def search_user(query: str) -> flask.Response:
    """
    Search for users by username.

    :param query: The search query to match against usernames.
    :return: JSON representation of a list of matching user data.
    """
    users: List[User] = User.query.filter(User.username.ilike(f'%{query}%')).all()
    return jsonify([user.serialized for user in users])
