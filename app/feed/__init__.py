from flask import Blueprint

feed_blueprint = Blueprint("feed", __name__)

from app.feed import routes
