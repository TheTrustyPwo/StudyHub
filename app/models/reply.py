import datetime

from app import db

from app.models.reply_vote import ReplyVote

class Reply(db.Model):
    """
    Model that represents a reply
    """
    __tablename__ = "replies"

    id = db.Column(db.Integer, primary_key=True)
    reply = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)

    reply_votes = db.relationship("ReplyVote", backref="reply", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Reply (id='{self.id}', reply='{self.reply}', date_created='{self.date_created}')>"

    def __init__(self, reply: str, user_id: int, post_id: int):
        self.reply = reply
        self.user_id = user_id
        self.post_id = post_id

    def save(self):
        """
        Persist the reply in the database
        :return
        """
        db.session.add(self)
        db.session.commit()

    @property
    def serialized(self):
        return {
            'id': self.id,
            'text': self.reply,
            'authorId': self.user_id,
            'postId': self.post_id,
            'timestamp': self.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            'votes': [vote.serialized for vote in self.reply_votes]
        }

    @staticmethod
    def get_by_id(reply_id):
        """
        Filter a reply by id
        :param reply_id
        :return: Reply or None
        """
        return Reply.query.filter_by(id=reply_id).first()

