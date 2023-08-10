from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_required

from app.ai import ai_blueprint
from app.ai.qna import services


@ai_blueprint.route('/ai/qna')
@login_required
def view_qna():
    return render_template('qna.html')
