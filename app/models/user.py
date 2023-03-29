import datetime

from flask_login import UserMixin
from passlib.hash import bcrypt

from app import db, login_manager
from app.models.post import Post
from app.models.reply import Reply
from app.models.post_vote import PostVote
from app.models.reply import ReplyVote


class User(db.Model, UserMixin):
    """
    Model that represents a user
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    posts = db.relationship("Post", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    replies = db.relationship("Reply", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    post_votes = db.relationship("PostVote", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    reply_votes = db.relationship("ReplyVote", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User (id='{self.id}', username='{self.username}' email='{self.email}')>"

    def __init__(self, email: str, username: str, password: str):
        self.email = email
        self.username = username
        self.password = password

    def save(self):
        """
        Persist the user in the database
        :return:
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    @login_manager.user_loader
    def load_user(user_id):
        """
        Loader used to reload the user object from the user ID stored in the session.
        https://flask-login.readthedocs.io/en/latest/#how-it-works
        """
        return User.query.get(user_id)

    @staticmethod
    def get_by_id(user_id):
        """
        Filter a user by Id.
        :param user_id
        :return: User or None
        """
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_by_email(email):
        """
        Check a user by their email address
        :param email:
        :return:
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_username(username):
        """
        Check a user by their username
        :param username:
        :return:
        """
        return User.query.filter_by(username=username).first()

    def reset_password(self, new_password):
        """
        Update/reset the user password.
        :param new_password: New User Password
        :return:
        """
        self.password = bcrypt.hash(new_password)
        db.session.commit()
