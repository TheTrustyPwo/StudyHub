from flask import Blueprint

messages_blueprint = Blueprint("messages", __name__)
messages_api_blueprint = Blueprint("messages_api", __name__, url_prefix='/api/v1/messages')

from app.messages import routes, api
