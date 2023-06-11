from flask_login import login_user, logout_user
from passlib.hash import bcrypt

from app.models import User


def register_user(email: str, username: str, password: str):
    """
    Hashes the given password and registers a new user in the database.

    :param email: The email of the user.
    :type email: str
    :param username: The username of the user.
    :type username: str
    :param password: The password of the user.
    :type password: str
    """
    hashed_password = bcrypt.hash(password)
    user = User(email=email.lower(), username=username, password=hashed_password)
    user.save()


def log_in_user(email, password):
    """
    Hashes and compares the given password with the stored password. If it is a match,
    logs a user in.

    :param email: The email of the user.
    :type email: str
    :param password: The password of the user.
    :type password: str
    :return: True if the login is successful, False otherwise.
    :rtype: bool
    """
    user = User.get_by_email(email.lower())
    if user and bcrypt.verify(password, user.password):
        login_user(user)
        return True
    return False


def log_out_user():
    """
    Logs the current user out.
    """
    logout_user()
