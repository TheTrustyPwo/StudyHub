from flask import jsonify
import json
from flask_login import current_user, login_required

from app.conversations import conversation_services
from app.exceptions import Unauthorized, NotFound
from app.post import post_api_blueprint

from app.models import Post

@post_api_blueprint.route("/<int:start_row>/<int:end_row>", methods=["GET"])
def get_post_by_range(start_row, end_row):
    out = []
    for i in Post.get_post_range(start_row, end_row):
        out.append({'ptitle': i.title, 'post': i.post, 'date': i.date_created, 'user': i.user_id, 'id': i.id})
    return out

@post_api_blueprint.route("/count", methods = ["GET"])
def get_post_count():
    return str(Post.query.count())