from typing import List

from flask import jsonify, Response, request
from flask_login import current_user, login_required

from app import db
from sqlalchemy import desc, func
from app.exceptions import Unauthorized, NotFound, BadRequest
from app.models import Post, PostVote, Subject
from app.post import post_api_blueprint
from app.upload.files import FilePurpose, PostAttachment


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


@post_api_blueprint.route('/all', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    before = request.args.get('before')
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
        query = query.filter(Post.date_created < datetime.datetime.strptime(before))

    if sort_by == 'latest':
        query = query.order_by(Post.date_created.desc())
    elif sort_by == 'popular':
        query = query.order_by(desc(func.sum(Post.post_votes.vote)).label('score')).all()

    posts = query.offset((page - 1) * limit).limit(limit).all()
    serialized_posts = [post.serialized for post in posts]
    return jsonify(serialized_posts), 200
