import datetime

from app import db

from app.models.reply import Reply
from app.models.post_vote import PostVote
from enum import Enum
from app.upload.files import File, FilePurpose


class Subject(Enum):
    ENGLISH = 'english'
    MATHEMATICS = 'mathematics'
    PHYSICS = 'physics'
    CHEMISTRY = 'chemistry'
    BIOLOGY = 'biology'
    SOCIAL_STUDIES = 'social_studies'
    GEOGRAPHY = 'geography'
    HISTORY = 'history'
    CHINESE = 'chinese'
    COMPUTING = 'computing'
    LITERATURE = 'literature'
    MUSIC = 'music'
    ART = 'art'

    @classmethod
    def has_key(cls, name):
        return name.upper() in cls.__members__

class Post(db.Model):
    """
    Model that represents a post
    """
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    post = db.Column(db.Text, nullable=False)
    subject = db.Column(db.Enum(Subject), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    attachment_name = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    replies = db.relationship("Reply", backref="post", lazy="dynamic", cascade="all, delete-orphan")
    post_votes = db.relationship("PostVote", backref="post", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post (id='{self.id}', title='{self.title}', post='{self.post}', subject='{self.subject.name}', date_created='{self.date_created}')>"

    def __init__(self, title: str, post: str, subject: Subject, user_id: int, attachment_name: str = None):
        self.title = title
        self.post = post
        self.subject = subject
        self.user_id = user_id
        self.attachment_name = attachment_name

    def save(self):
        """
        Persist the post in the database
        :return
        """
        db.session.add(self)
        db.session.commit()

    @property
    def post_score(self):
        upvotes = sum(vote.vote for vote in self.post_votes if vote.vote == 1)
        downvotes = sum(vote.vote for vote in self.post_votes if vote.vote == -1)
        return upvotes - downvotes

    @property
    def attachment(self):
        if not self.attachment_name:
            return None
        return File.get(self.attachment_name, FilePurpose.POST_ATTACHMENT, self.user_id)

    @property
    def serialized(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.post,
            'subject': self.subject.name,
            'authorId': self.user_id,
            'timestamp': self.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            'votes': [vote.serialized for vote in self.post_votes],
            'replyCount': len(list(self.replies)),
            'attachment': self.attachment
        }

    @staticmethod
    def get_by_id(post_id):
        """
        Filter a post by id
        :param post_id
        :return: User or None
        """
        return Post.query.filter_by(id=post_id).first()
