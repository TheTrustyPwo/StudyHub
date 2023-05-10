from flask import Blueprint

conversations_blueprint = Blueprint("conversations", __name__)
conversations_api_blueprint = Blueprint("conversations_api", __name__, url_prefix='/api/v1/conversations')

from app.conversations import routes, api
