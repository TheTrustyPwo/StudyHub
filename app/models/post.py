import datetime

from app import db

from app.models.reply import Reply
from app.models.post_vote import PostVote


class Post(db.Model):
    """
    Model that represents a post
    """
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    post = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    replies = db.relationship("Reply", backref="post", lazy="dynamic", cascade="all, delete-orphan")
    post_votes = db.relationship("PostVote", backref="post", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post (id='{self.id}', title='{self.title}', post='{self.post}', date_created='{self.date_created}')>"

    def __init__(self, title: str, post: str, user_id: int):
        self.title = title
        self.post = post
        self.user_id = user_id

    def save(self):
        """
        Persist the post in the database
        :return
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(post_id):
        """
        Filter a post by id
        :param post_id
        :return: User or None
        """
        return Post.query.filter_by(id=post_id).first()
