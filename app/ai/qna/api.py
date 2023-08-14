import bleach
from flask import request, jsonify
from flask_login import current_user

from app.ai import ai_api_blueprint
from app.ai.qna import services


@ai_api_blueprint.route('/qna/answer', methods=['POST'])
def answer_question():
    if current_user.credits <= 0:
        return Forbidden(message='User does not have enough credits left')
    current_user.credits -= 1
    current_user.save()

    question = bleach.clean(request.json.get('question'))
    answer = services.answer(question)
    return jsonify({'answer': answer}), 200
