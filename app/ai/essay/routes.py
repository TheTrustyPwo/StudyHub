import bleach
from flask import render_template, redirect, url_for
from flask_login import current_user, login_required

from app.ai import ai_blueprint
from app.ai.essay import services
from app.ai.essay.forms import GradeEssayForm
from app.exceptions import Forbidden
from app.models import Essay


@ai_blueprint.route('/ai/essay', methods=['GET', 'POST'])
@login_required
def grade_essay():
    form = GradeEssayForm()

    if form.validate_on_submit():
        if current_user.credits <= 0:
            return Forbidden(message='User does not have enough credits left')
        current_user.credits -= 1
        current_user.save()

        title = bleach.clean(form.title.data)
        content = bleach.clean(form.content.data)

        essay = services.grade_essay(title, content, current_user.id)

        return redirect(url_for('ai.view_essay', essay_id=essay.id))

    return render_template('essay_home.html', form=form)


@ai_blueprint.route('/ai/essay/<int:essay_id>')
def view_essay(essay_id: int):
    Essay.query.filter_by(id=essay_id).first_or_404()
    return render_template('essay.html')
