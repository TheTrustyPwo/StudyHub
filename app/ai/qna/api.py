from flask import render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required

from app.ai import ai_api_blueprint
from app.ai.qna import services


@ai_api_blueprint.route('/qna/answer', methods=['POST'])
def answer_question():
    question = request.json["question"]
    answer = services.answer(question)
    return jsonify({'answer': answer}), 200
