from flask import Blueprint

messages_blueprint = Blueprint("messages", __name__)

from app.messages import routes
