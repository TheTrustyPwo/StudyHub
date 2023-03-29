from app import db
from app.models import User, Post, PostVote, Reply, ReplyVote


def create_post(title: str, data: str, user_id: int):
    """
    Create a post, save it, and return the post id
    """
    post = Post(title, data, user_id)
    post.save()
    return post.id


def get_post_with_votes(post_id: int):
    """
    Gets a post with vote information by id from database
    """
    post = (
        db.session.query(
            Post.id, Post.title, Post.post, Post.date_created, Post.user_id,
            db.func.coalesce(db.func.sum(PostVote.vote), 0).label("votes"), User.username
        )
        .join(User, Post.user_id == User.id).outerjoin(PostVote, Post.id == PostVote.post_id)
        .filter(Post.id == post_id).group_by(Post.id, AppUser.id).first()
    )
    return post


def get_post_replies(post_id: int, page: int, ordered_by_votes: bool = False):
    """
    Gets paginated list of replies for a specified post from the database
    """
    ordered_by = Reply.date_created.desc()
    if ordered_by_votes:
        ordered_by = db.literal_column("votes").desc()

    replies = (
        db.session.query(
            Reply.id, Reply.reply, Reply.user_id, Reply.date_created,
            db.func.coalesce(db.func.sum(ReplyVote.vote), 0).label("votes"), User.username,
        )
        .join(User, Reply.user_id == User.id).outerjoin(ReplyVote, Reply.id == ReplyVote.reply_id)
        .filter(Reply.post_id == post_id).group_by(Reply.id, User.id)
        .order_by(ordered_by).paginate(page=page, per_page=5)
    )
    return replies


def get_post_vote(post_id: int, user_id: int):
    """
    Gets a specific user's vote on a post the database
    """
    post_vote = PostVote.query.filter_by(user_id=user_id, post_id=post_id).first()
    return post_vote


def upvote_post(post_id: int, user_id: int):
    """
    Upvote a post for a user in the database
    If the user has already voted for the post, it is undone
    """
    post_vote = get_post_vote(post_id, user_id)
    if post_vote is None:
        post_vote = PostVote(vote=1, user_id=user_id, post_id=post_id)
    elif abs(post_vote.vote) == 1:
        post_vote.vote = 0
    else:
        post_vote.vote = 1
    post_vote.save()


def downvote_post(post_id: int, user_id: int):
    """
    Downvote a post for a user in the database
    If the user has already downvoted the post, it is undone
    """
    post_vote = get_post_vote(post_id, user_id)
    if post_vote is None:
        post_vote = PostVote(vote=-1, user_id=user_id, post_id=post_id)
    elif abs(post_vote.vote) == 1:
        post_vote.vote = 0
    else:
        post_vote.vote = -1
    post_vote.save()


def delete_post(post):
    """
    Removes a post from the database.
    """
    db.session.delete(post)
    db.session.commit()
