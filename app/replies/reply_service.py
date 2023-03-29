from app import db
from app.models import Reply, ReplyVote


def create_reply(reply: str, post_id: int, user_id: int):
    """
    Adds a new reply to the database
    """
    reply = Reply(reply=reply, post_id=post_id, user_id=user_id)
    reply.save()


def update_reply(reply: Reply, reply_text: str):
    """
    Updates a reply's text content in the database
    """
    reply.reply = reply_text
    reply.save()


def delete_reply(reply: Reply):
    """
    Removes a reply from the database
    """
    db.session.delete(reply)
    db.session.commit()


def get_reply_vote(reply_id: int, user_id: int):
    """
    Gets a specific user's vote on a reply the database
    """
    reply_vote = ReplyVote.query.filter_by(user_id=user_id, reply_id=reply_id).first()
    return reply_vote


def upvote_reply(reply_id: int, user_id: int):
    """
    Upvote a reply for a user in the database
    If user has already voted on the reply, it is undone
    """
    reply_vote = get_reply_vote(reply_id, user_id)
    if reply_vote is None:
        reply_vote = ReplyVote(vote=1, user_id=user_id, reply_id=reply_id)
    elif abs(reply_vote.vote) == 1:
        reply_vote.vote = 0
    else:
        reply_vote.vote = 1
    reply_vote.save()


def downvote_reply(reply_id: int, user_id: int):
    """
    Downvote a reply for a user in the database
    If user has already voted on the reply, it is undone
    """
    reply_vote = get_reply_vote(reply_id, user_id)
    if reply_vote is None:
        reply_vote = ReplyVote(vote=-1, user_id=user_id, reply_id=reply_id)
    elif abs(reply_vote.vote) == 1:
        reply_vote.vote = 0
    else:
        reply_vote.vote = -1
    reply_vote.save()
