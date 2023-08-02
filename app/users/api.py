from typing import List

import flask
from flask import jsonify, request
from flask_login import current_user, login_required

from app.exceptions import BadRequest, NotFound
from app.models import User
from app.upload.files import ProfileFile
from app.users import user_api_blueprint


@user_api_blueprint.route("/current")
@login_required
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


@user_api_blueprint.route('/pfp/upload', methods=['POST'])
@login_required
def upload_pfp() -> flask.Response:
    file_data = request.files['file']
    if not file_data:
        raise BadRequest(message='Upload must contain file')

    image = ProfileFile(file_data, current_user.id)
    url = image.upload()

    current_user.pfp_file_name = image.filename
    current_user.save()

    return jsonify({'url': url})
