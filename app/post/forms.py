from flask_wtf import FlaskForm
from wtforms.fields import IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError


class PostForm(FlaskForm):
    """
    Form for creating a new post
    """

    title = StringField("Title", validators=[DataRequired()])
    post = TextAreaField("Post", validators=[DataRequired()])
    submit = SubmitField("Create")


class UpdatePostForm(FlaskForm):
    """
    Form for updating a post
    """

    post = TextAreaField("Post", validators=[DataRequired()])
    submit = SubmitField("Create")
