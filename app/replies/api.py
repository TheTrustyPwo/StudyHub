from flask import redirect, url_for, jsonify, request
from flask_login import current_user, login_required
from app import db

from app.replies import reply_api_blueprint
from app.exceptions import Unauthorized, NotFound, BadRequest
from app.models import Reply, ReplyVote, Post


@reply_api_blueprint.route('/<int:reply_id>')
def get_reply(reply_id: int):
    reply = Reply.get_by_id(reply_id)
    if not reply:
        raise NotFound(message='Reply not found')

    return jsonify(reply.serialized)


@reply_api_blueprint.route('/create', methods=['POST', 'GET'])
@login_required
def create_reply():
    post_id = request.json.get('post_id')
    if post_id is None:
        raise BadRequest(message='Reply must contain post_id')

    if not Post.get_by_id(post_id):
        raise NotFound(message='Post does not exist')

    text = request.json.get('reply')
    if text is None or len(text) == 0:
        raise BadRequest(message='Reply must contain text')

    reply = Reply(text, current_user.id, post_id)
    reply.save()

    return jsonify(reply.serialized)


@reply_api_blueprint.route('/<int:reply_id>/upvote', methods=['POST', 'GET'])
@login_required
def upvote_reply(reply_id: int):
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
def downvote_reply(reply_id: int):
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
def delete_reply(reply_id: int):
    reply = Reply.get_by_id(reply_id)
    if not reply:
        raise NotFound(message='Reply not found')

    if reply.user_id != current_user.id:
        raise Unauthorized(message="Cannot delete other people's replies")

    db.session.delete(reply)
    db.session.commit()
