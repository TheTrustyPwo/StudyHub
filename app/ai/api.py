import datetime

from flask import request, jsonify, Response
from flask_login import current_user, login_required

from app.ai import ai_api_blueprint, ai_services
from app.exceptions import BadRequest, Unauthorized, NotFound, Conflict
from app.models import User, Essay, EssayCriticism, EssayEvaluation, EssayCompliment


@ai_api_blueprint.route('/essay/<int:essay_id>')
@login_required
def get_essay(essay_id: int):
    essay = Essay.get_by_id(essay_id)
    if not essay:
        raise NotFound(message='Essay not found')

    if essay.user_id != current_user.id:
        raise Unauthorized(message='This essay is not yours')

    return jsonify(essay.serialized)


@ai_api_blueprint.route('/essay/all')
@login_required
def get_all_essays():
    essays = [essay.serialized for essay in list(current_user.essays)]
    return jsonify(essays)


@ai_api_blueprint.route('/essay/grade', methods=['POST'])
@login_required
def grade_essay() -> Response:
    topic = request.json.get('topic')
    if not topic:
        raise BadRequest(message='Topic not present')

    essay = request.json.get('essay')
    if not essay:
        raise BadRequest(message='Essay not present')

    essay = ai_services.grade_essay(topic, essay, current_user.id)
    return jsonify(essay.serialized)
