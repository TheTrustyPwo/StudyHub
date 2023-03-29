from app import db


class ReplyVote(db.Model):
    """
    Model that represents a user's vote on a post
    """
    __tablename__ = "reply_votes"

    id = db.Column(db.Integer, primary_key=True)
    vote = db.Column(db.SmallInteger, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reply_id = db.Column(db.Integer, db.ForeignKey("replies.id"), nullable=False)

    def __repr__(self):
        return f"<ReplyVote (id='{self.id}', vote='{self.vote}')>"

    def __init__(self, vote: int, user_id: int, reply_id: int):
        self.vote = vote
        self.user_id = user_id
        self.reply_id = reply_id

    def save(self):
        """
        Persist the post vote in the database
        :return
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(reply_vote_id):
        """
        Filter a reply vote by id
        :param reply_vote_id
        :return: ReplyVote or None
        """
        return ReplyVote.query.filter_by(id=reply_vote_id).first()
