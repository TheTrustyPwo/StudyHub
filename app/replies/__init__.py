from flask import Blueprint

reply_blueprint = Blueprint('reply', __name__)
reply_api_blueprint = Blueprint('reply_api', __name__, url_prefix='/api/v1/replies')

from app.replies import api
