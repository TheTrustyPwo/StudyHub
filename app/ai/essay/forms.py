from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length


class GradeEssayForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=150)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=1, max=15000)])
