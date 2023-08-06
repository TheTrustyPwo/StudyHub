from typing import List

from flask import jsonify, Response, request
from flask_login import current_user, login_required

from app import db
from app.exceptions import Unauthorized, NotFound, BadRequest
from app.models import Post, PostVote, Subject
from app.post import post_api_blueprint


@post_api_blueprint.route('/create', methods=['POST', 'GET'])
@login_required
def create_post() -> Response:
    """
    Create a new post.

    :return: JSON representation of the created post data.
    :raises BadRequest: If the request does not contain title or body.
    """
    title = request.json.get('title')
    if not title:
        raise BadRequest(message='Post must contain title')

    body = request.json.get('body')
    if not body:
        raise BadRequest(message='Post must contain body')

    subject = request.json.get('subject')
    if not subject or not Subject.has_key(subject):
        raise BadRequest(message='Invalid post subject')

    post = Post(title=title, post=body, subject=Subject(subject), user_id=current_user.id)
    post.save()

    return jsonify(post.serialized)


@post_api_blueprint.route('/search/<string:query>')
def search_post(query: str) -> Response:
    """
    Search for posts.

    :param query: The search query to match against posts.
    :return: JSON representation of a list of matching post data.
    """
    posts: List[Post] = Post.query.filter(Post.title.ilike(f'%{query}%')).all()
    return jsonify([post.serialized for post in posts])


@post_api_blueprint.route('/<int:post_id>')
def get_post(post_id: int) -> Response:
    """
    Get post data by post ID.

    :param post_id: The ID of the post to retrieve.
    :return: JSON representation of the post data.
    """
    post = Post.get_by_id(post_id)
    if not post:
        raise NotFound(message='Post not found')

    return jsonify(post.serialized)


@post_api_blueprint.route('/<int:post_id>/replies')
def get_post_replies(post_id: int) -> Response:
    """
    Get replies to a post by post ID.

    :param post_id: The ID of the post to retrieve replies for.
    :return: JSON representation of a list of reply data.
    """
    post = Post.get_by_id(post_id)
    if not post:
        raise NotFound(message='Post not found')

    return jsonify([reply.serialized for reply in post.replies])


@post_api_blueprint.route('/<int:post_id>/upvote', methods=['POST', 'GET'])
@login_required
def upvote_post(post_id: int) -> Response:
    """
    Upvote a post.

    :param post_id: The ID of the post to upvote.
    :return: JSON representation of the updated post data.
    """
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
def downvote_post(post_id: int) -> Response:
    """
    Downvote a post.

    :param post_id: The ID of the post to downvote.
    :return: JSON representation of the updated post data.
    """
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
def delete_post(post_id: int) -> None:
    """
    Delete a post.

    :param post_id: The ID of the post to delete.
    """
    post = Post.get_by_id(post_id)
    if not post:
        raise NotFound(message='Post not found')

    if post.user_id != current_user.id:
        raise Unauthorized(message="Cannot delete other people's posts")

    db.session.delete(post)
    db.session.commit()

@post_api_blueprint.route("/latest/<int:user_id>", methods=["GET"])
def get_most_recent_post(user_id):
    """
    Get the latest post of a user

    :param user_id: The ID of the user
    """
    post = Post.get_most_recent_by_user(user_id)
    if not post:
        raise NotFound(message='User has not created a post yet')
    return jsonify(post.serialized)

@post_api_blueprint.route("/<int:start_row>/<int:end_row>", methods=["GET"])
def get_post_by_range(start_row: int, end_row: int) -> List[dict]:
    """
    Get posts within a specified range.

    :param start_row: The starting row of the range.
    :param end_row: The ending row of the range.
    :return: List of dictionaries containing post data within the range.
    """
    # @Stucknight TODO: Please use jsonify and use post.serialized
    out = []
    for i in Post.get_post_range(start_row, end_row):
        out.append({'ptitle': i.title, 'post': i.post, 'date': i.date_created, 'user': i.user_id, 'id': i.id})
    return out


@post_api_blueprint.route("/count", methods=["GET"])
def get_post_count() -> str:
    """
    Get the total count of posts.

    :return: The count of posts as a string.
    """
    return str(Post.query.count())
