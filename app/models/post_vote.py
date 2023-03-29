from app import db


class PostVote(db.Model):
    """
    Model that represents a user's vote on a post
    """
    __tablename__ = "post_votes"

    id = db.Column(db.Integer, primary_key=True)
    vote = db.Column(db.SmallInteger, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)

    def __repr__(self):
        return f"<PostVote (id='{self.id}', vote='{self.vote}')>"

    def __init__(self, vote: int, user_id: int, post_id: int):
        self.vote = vote
        self.user_id = user_id
        self.post_id = post_id

    def save(self):
        """
        Persist the post vote in the database
        :return
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(post_vote_id):
        """
        Filter a post vote by id
        :param post_vote_id
        :return: PostVote or None
        """
        return PostVote.query.filter_by(id=post_vote_id).first()
