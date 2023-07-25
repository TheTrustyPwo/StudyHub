from flask import jsonify
from flask_login import current_user, login_required

from app import db
from app.exceptions import Unauthorized, NotFound
from app.models import Post, PostVote
from app.post import post_api_blueprint


@post_api_blueprint.route('/<int:post_id>')
def get_post(post_id: int):
    post = Post.get_by_id(post_id)
    if not post:
        raise NotFound(message='Post not found')

    return jsonify(post.serialized)


@post_api_blueprint.route('/<int:post_id>/replies')
def get_post_replies(post_id: int):
    post = Post.get_by_id(post_id)
    if not post:
        raise NotFound(message='Post not found')

    return jsonify([reply.serialized for reply in post.replies])


@post_api_blueprint.route('/<int:post_id>/upvote', methods=['POST', 'GET'])
@login_required
def upvote_post(post_id: int):
    post = Post.get_by_id(post_id)
    if not post:
        raise NotFound(message='Post not found')

    post_vote = PostVote.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if post_vote is None:
        post_vote = PostVote(vote=1, user_id=current_user.id, post_id=post_id)
    elif post_vote.vote == -1 or post_vote.vote == 0:
        post_vote.vote = 1
    else:
        post_vote.vote = 0
    post_vote.save()

    return jsonify(post.serialized)


@post_api_blueprint.route('/<int:post_id>/downvote', methods=['POST', 'GET'])
@login_required
def downvote_post(post_id: int):
    post = Post.get_by_id(post_id)
    if not post:
        raise NotFound(message='Post not found')

    post_vote = PostVote.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if post_vote is None:
        post_vote = PostVote(vote=-1, user_id=current_user.id, post_id=post_id)
    elif post_vote.vote == 1 or post_vote.vote == 0:
        post_vote.vote = -1
    else:
        post_vote.vote = 0
    post_vote.save()

    return jsonify(post.serialized)


@post_api_blueprint.route('/<int:post_id>/delete', methods=['DELETE'])
@login_required
def delete_post(post_id: int):
    post = Post.get_by_id(post_id)
    if not post:
        raise NotFound(message='Post not found')

    if post.user_id != current_user.id:
        raise Unauthorized(message="Cannot delete other people's posts")

    db.session.delete(post)
    db.session.commit()