from flask import render_template, redirect, url_for
from flask_login import current_user, login_required

from app.ai import ai_blueprint
from app.ai.essay import services
from app.ai.essay.forms import GradeEssayForm
from app.models import Essay


@ai_blueprint.route('/ai/essay', methods=['GET', 'POST'])
@login_required
def grade_essay():
    form = GradeEssayForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        essay = services.grade_essay(title, content, current_user.id)

        return redirect(url_for('ai.view_essay', essay_id=essay.id))

    return render_template('essay_home.html', form=form)


@ai_blueprint.route('/ai/essay/<int:essay_id>')
def view_essay(essay_id: int):
    Essay.query.filter_by(id=essay_id).first_or_404()
    return render_template('essay.html')