import re

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, EmailField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length, Email

from app.models import User


def check_email_registered(form, email: EmailField):
    """
    Validates that the email has not already been registered
    """
    user = User.get_by_email(email.data.lower())
    if user is not None:
        raise ValidationError('Email is already registered.')


def check_username_registered(form, username: StringField):
    """
    Validates that the provided username does not already exist in the database
    """
    user = User.get_by_username(username.data.lower())
    if user is not None:
        raise ValidationError('Username is already taken.')


def check_password_security(form, password: PasswordField):
    if len(password.data) < 8:
        raise ValidationError('Password must be at least 8 characters.')

    # Check if the password contains at least one uppercase letter
    if not any(c.isupper() for c in password.data):
        raise ValidationError('Password must contain at least 1 uppercase letter.')

    # Check if the password contains at least one lowercase letter
    if not any(c.islower() for c in password.data):
        raise ValidationError('Password must contain at least 1 lowercase letter.')

    # Check if the password contains at least one digit
    if not any(c.isdigit() for c in password.data):
        raise ValidationError('Password must contain at least 1 digit.')

    # Check if the password contains at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password.data):
        raise ValidationError('Password must contain at least 1 symbol.')


class RegisterForm(FlaskForm):
    """
    Form for registering a new user
    """

    username: StringField = StringField("Username", validators=[DataRequired(), check_username_registered])
    email: EmailField = EmailField("Email", validators=[DataRequired(), check_email_registered])
    password: PasswordField = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="Passwords must match."),
            Length(min=8)
        ],
    )
    confirm_password: PasswordField = PasswordField("Confirm Password", validators=[DataRequired()])
    submit: SubmitField = SubmitField("Register")


class LoginForm(FlaskForm):
    """
    Form for logging in a user
    """

    email: EmailField = EmailField("Email", validators=[DataRequired()])
    password: PasswordField = PasswordField("Password", validators=[DataRequired()])
    submit: SubmitField = SubmitField("Login")
