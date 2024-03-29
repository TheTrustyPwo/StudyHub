from flask import Blueprint

ai_blueprint = Blueprint('ai', __name__)
ai_api_blueprint = Blueprint("ai_api", __name__, url_prefix='/api/v1/ai')

from app.ai.essay import api, routes
from app.ai.qna import api, routes
