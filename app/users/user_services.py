from typing import List

import flask
from flask import jsonify, request
from flask_login import current_user, login_required

from app.exceptions import BadRequest, NotFound
from app.models import User
from app.upload.files import ProfileFile
from app.users import user_api_blueprint


def update_pfp(user_id: int, file):
    user = User.get_by_id(user_id)
    if not user:
        return None

    image = ProfileFile(file, user.id)
    url = image.upload()
    user.pfp_file_name = image.filename
    user.save()

    return url
