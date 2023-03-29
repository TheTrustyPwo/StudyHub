from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length

from app.models import User


class RegisterForm(FlaskForm):
    """
    Form for registering a new user
    """

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="Passwords must match."),
            Length(min=6),
        ],
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, email):
        """
        Validates that the email has not already been registered
        """
        user = User.get_by_email(email.data.lower())
        if user is not None:
            raise ValidationError("Email is already registered.")

    def validate_username(self, username):
        """
        Validates that the provided username does not already exist in the database
        """
        user = User.get_by_username(username.data.lower())
        if user is not None:
            raise ValidationError("Username is already taken.")


class LoginForm(FlaskForm):
    """
    Form for logging in a user
    """

    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
