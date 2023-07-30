from flask import Blueprint

post_blueprint = Blueprint("post", __name__)
post_api_blueprint = Blueprint("post_api", __name__, url_prefix='/api/v1/post')

from app.post import routes, api
