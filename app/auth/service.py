from flask_login import login_user, logout_user

from app import app
from app import bcrypt
from app.models import User


def register_user(email: str, username: str, password: str):
    """
    Hashes the given password and registers a new user in the database.
    """
    hashed_password = bcrypt.generate_password_hash(password, rounds=app.config.get('BCRYPT_HASH_PREFIX'),
                                                    prefix=b'2b').decode('utf-8')
    user = User(email=email.lower(), username=username, password=hashed_password)
    user.save()


def log_in_user(email, password):
    """
    Hashes and compares the given password with the stored password. If it is a match,
    logs a user in.
    """
    user = User.get_by_email(email.lower())
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return True
    else:
        return False


def log_out_user():
    """
    Logs the current user out.
    """
    logout_user()
