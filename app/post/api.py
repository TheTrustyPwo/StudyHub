from datetime import datetime
from typing import List, Tuple

from flask import jsonify, Response, request
from flask_login import current_user, login_required
from sqlalchemy import desc, func

from app import db
from app.exceptions import Unauthorized, NotFound, BadRequest
from app.models import Post, PostVote, Subject, Reply
from app.post import post_api_blueprint
from app.upload.files import PostAttachment


@post_api_blueprint.route('/create', methods=['POST', 'GET'])
@login_required
def create_post() -> Response:
    """
    Create a new post.

    :return: JSON representation of the created post data.
    :raises BadRequest: If the request does not contain title or body.
    """
    title = request.form.get('title')
    if not title:
        raise BadRequest(message='Post must contain title')

    body = request.form.get('body')
    if not body:
        raise BadRequest(message='Post must contain body')

    subject = request.form.get('subject')
    if not subject or not Subject.has_key(subject):
        raise BadRequest(message='Invalid post subject')

    attachment = request.files.get('file', None)
    filename = None
    if attachment:
        image = PostAttachment(attachment, current_user.id)
        image.upload()
        filename = image.filename

    post = Post(title=title, post=body, subject=Subject(subject), user_id=current_user.id, attachment_name=filename)
    post.save()

    return jsonify(post.serialized)


@post_api_blueprint.route('/search')
def search_post() -> Response:
    query = request.args.get('query')
    limit = request.args.get('limit', type=int, default=5)
    posts: List[Post] = Post.query.filter(Post.title.ilike(f'%{query}%')).limit(limit).all()
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
def delete_post(post_id: int) -> tuple[Response, int]:
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

    return jsonify({'message': 'Post deleted'}), 200

@post_api_blueprint.route('/user', methods=['GET'])
def get_user_posts():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    user_id = int(request.args.get('id'))

    start_index = (page - 1) * limit
    end_index = start_index + limit

    posts = Post.query.filter_by(user_id=user_id).order_by(Post.date_created.desc()).slice(start_index, end_index).all()
    serialized_posts = [post.serialized for post in posts]
    return jsonify(serialized_posts), 200


@post_api_blueprint.route('<int:post_id>/resolve', methods=['POST', 'GET'])
def resolve(post_id: int):
    post = Post.get_by_id(post_id)
    if not post:
        raise NotFound(message='Post not found')
    if post.resolved_by_id:
        raise BadRequest(message='Post already resolved')
    if post.user_id != current_user.id:
        raise Unauthorized(message='Cannot resolve other user\'s posts')

    reply_id = request.args.get('reply_id', type=int)
    if not reply_id:
        raise BadRequest(message='Reply ID not specified')

    reply = Reply.get_by_id(reply_id)
    if not reply:
        raise NotFound(message='Reply not found')
    if reply.post_id != post.id:
        raise BadRequest(message='Reply does not belong to post')

    post.resolved_by_id = reply.id
    post.save()

    reply.user.answered += 1
    reply.user.save()

    return jsonify(post.serialized), 200


@post_api_blueprint.route('/all', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    before = request.args.get('before', type=int)
    subjects = request.args.get('subjects')
    sort_by = request.args.get('sort', 'latest').lower()

    if subjects:
        subjects = list(map(str.upper, subjects.split(',')))
        if 'ALL SUBJECTS' in subjects:
            subjects = None

    query = Post.query
    if subjects:
        query = query.filter(Post.subject.in_(subjects))

    if before:
        query = query.filter(Post.date_created < datetime.fromtimestamp(before))

    if sort_by == 'latest':
        query = query.order_by(Post.date_created.desc())

    posts = query.paginate(page=page, per_page=limit).items
    serialized_posts = [post.serialized for post in posts]
    return jsonify(serialized_posts), 200
