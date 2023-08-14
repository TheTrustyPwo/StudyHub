import bleach
from flask import jsonify, request, Response
from flask_login import current_user, login_required

from app import db
from app.exceptions import Unauthorized, NotFound, BadRequest
from app.models import Reply, ReplyVote, Post
from app.replies import reply_api_blueprint


@reply_api_blueprint.route('/<int:reply_id>')
def get_reply(reply_id: int) -> Response:
    """
    Get reply data by reply ID.

    :param reply_id: The ID of the reply to retrieve.
    :return: JSON representation of the reply data.
    """
    reply = Reply.get_by_id(reply_id)
    if not reply:
        raise NotFound(message='Reply not found')

    return jsonify(reply.serialized)


@reply_api_blueprint.route('/create', methods=['POST', 'GET'])
@login_required
def create_reply() -> Response:
    """
    Create a new reply.

    :return: JSON representation of the created reply data.
    :raises BadRequest: If the request does not contain post_id or reply text.
    :raises NotFound: If the post with the provided post_id does not exist.
    """
    post_id = request.json.get('post_id')
    if post_id is None:
        raise BadRequest(message='Reply must contain post_id')

    if not Post.get_by_id(post_id):
        raise NotFound(message='Post does not exist')

    text = request.json.get('reply')
    if text is None or len(text) == 0:
        raise BadRequest(message='Reply must contain text')

    reply = Reply(bleach.clean(text), current_user.id, post_id)
    reply.save()

    return jsonify(reply.serialized)


@reply_api_blueprint.route('/<int:reply_id>/upvote', methods=['POST', 'GET'])
@login_required
def upvote_reply(reply_id: int) -> Response:
    """
    Upvote a reply.

    :param reply_id: The ID of the reply to upvote.
    :return: JSON representation of the updated reply data.
    """
    reply = Reply.get_by_id(reply_id)
    if not reply:
        raise NotFound(message='Reply not found')

    reply_vote = ReplyVote.query.filter_by(user_id=current_user.id, reply_id=reply_id).first()
    if reply_vote is None:
        reply_vote = ReplyVote(vote=1, user_id=current_user.id, reply_id=reply_id)
    elif reply_vote.vote == -1 or reply_vote.vote == 0:
        reply_vote.vote = 1
    else:
        reply_vote.vote = 0
    reply_vote.save()

    return jsonify(reply.serialized)


@reply_api_blueprint.route('/<int:reply_id>/downvote', methods=['POST', 'GET'])
@login_required
def downvote_reply(reply_id: int) -> Response:
    """
    Downvote a reply.

    :param reply_id: The ID of the reply to downvote.
    :return: JSON representation of the updated reply data.
    """
    reply = Reply.get_by_id(reply_id)
    if not reply:
        raise NotFound(message='Reply not found')

    reply_vote = ReplyVote.query.filter_by(user_id=current_user.id, reply_id=reply_id).first()
    if reply_vote is None:
        reply_vote = ReplyVote(vote=-1, user_id=current_user.id, reply_id=reply_id)
    elif reply_vote.vote == 1 or reply_vote.vote == 0:
        reply_vote.vote = -1
    else:
        reply_vote.vote = 0
    reply_vote.save()

    return jsonify(reply.serialized)


@reply_api_blueprint.route('/<int:reply_id>/delete', methods=['DELETE'])
@login_required
def delete_reply(reply_id: int) -> None:
    """
    Delete a reply.

    :param reply_id: The ID of the reply to delete.
    :raises NotFound: If the reply with the provided ID does not exist.
    :raises Unauthorized: If the current user is not the owner of the reply.
    """
    reply = Reply.get_by_id(reply_id)
    if not reply:
        raise NotFound(message='Reply not found')

    if reply.user_id != current_user.id:
        raise Unauthorized(message="Cannot delete other people's replies")

    db.session.delete(reply)
    db.session.commit()
