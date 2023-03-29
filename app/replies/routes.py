from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import Reply
from app.post import post_service
from app.replies import reply_blueprint, reply_service
from app.replies.forms import ReplyForm
from app.models import Post


@reply_blueprint.route("/post/<int:post_id>/reply", methods=["GET", "POST"])
@login_required
def create_reply(post_id: int):
    """
    Route for creating a reply. On a GET request, it returns the reply creation form
    On a POST request, it handles creating a reply
    """
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)

    form = ReplyForm()
    if form.validate_on_submit():
        reply_service.create_reply(form.reply.data, post.id, current_user.id)
        flash("Successfully created reply.", "primary")
        return redirect(url_for("post.view_post", post_id=post_id))
    return render_template("create_reply.html", post=post, form=form)


@reply_blueprint.route("/post/<int:post_id>/reply/<int:reply_id>/delete", methods=["POST"])
@login_required
def delete_reply(post_id: int, reply_id: int):
    """
    Route that handles deleting a reply
    """
    reply = Reply.get_by_id(reply_id)
    if not reply:
        abort(404)

    if reply.user_id != current_user.id:
        return redirect(url_for("post.view_post", post_id=post_id))
    reply_service.delete_reply(reply)
    flash("Successfully deleted reply.", "primary")
    return redirect(url_for("post.view_post", post_id=post_id))


@reply_blueprint.route("/post/<int:post_id>/reply/<int:reply_id>/upvote", methods=["POST"])
@login_required
def upvote_reply(post_id: int, reply_id: int):
    """
    Route that handles upvoting a reply as the current user
    """
    reply = Reply.get_by_id(reply_id)
    if not reply:
        abort(404)

    reply_service.upvote_reply(reply_id, current_user.id)
    return redirect(request.referrer)


@reply_blueprint.route("/post/<int:post_id>/reply/<int:reply_id>/downvote", methods=["POST"])
@login_required
def downvote_reply(post_id: int, reply_id: int):
    """
    Route that handles downvoting a reply as the current user
    """
    reply = Reply.get_by_id(reply_id)
    if not reply:
        abort(404)

    reply_service.downvote_reply(reply_id, current_user.id)
    return redirect(request.referrer)
