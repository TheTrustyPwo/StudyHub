from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=80)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=1, max=2000)])
    subject = SelectField('Subject', choices=[('english', 'English'), ('mathematics', 'Mathematics'), ('physics', 'Physics'), ('chemistry', 'Chemistry'), ('biology', 'Biology'), ('social_studies', 'Social Studies'), ('geography', 'Geography'), ('history', 'History'), ('chinese', 'Chinese'), ('computing', 'Computing'), ('literature', 'Literature'), ('music', 'Music'), ('art', 'Art')])
    attachment = FileField('Attachment', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx'])])
