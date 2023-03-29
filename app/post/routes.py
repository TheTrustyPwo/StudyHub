from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.post import post_blueprint, post_service
from app.models import Post
from app.post.forms import PostForm, UpdatePostForm

@post_blueprint.route("/post/<int:post_id>")
def view_post(post_id):
    """
    Route for page displaying a post and its replies sorted by date created.
    """
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)

    page = int(request.args.get("page", 1))
    replies = post_service.get_post_replies(post.id, page, False)
    return render_template("post.html", tab="recent", post=post, replies=replies)

@post_blueprint.route("/post/create", methods=["GET", "POST"])
@login_required
def create_post():
    """
    Route for creating a post. On a GET request, it returns the post creation form. On
    a POST request, it handles creating a post.
    """
    form = PostForm()
    if form.validate_on_submit():
        post_id = post_service.create_post(form.title.data, form.post.data, current_user.id)
        flash("Successfully created post", "primary")
        return redirect(url_for("post.view_post", post_id=post_id))
    return render_template("create_post.html", form=form)

@post_blueprint.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    """
    Route that handles deleting a post.
    """
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)

    if post.user_id != current_user.id:
        return redirect(url_for("post.view_post", post_id=post_id))
    post_service.delete_post(post)
    flash("Successfully deleted post", "primary")
    return redirect(url_for("home"))

@post_blueprint.route("/post/<int:post_id>/upvote", methods=["POST"])
@login_required
def upvote_post(post_id: int):
    """
    Route that handles upvoting a post as the current user
    """
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)

    post_service.upvote_post(post.id, current_user.id)
    return redirect(request.referrer)


@post_blueprint.route("/post/<int:post_id>/downvote", methods=["POST"])
@login_required
def downvote_post(post_id: int):
    """
    Route that handles downvoting a post as the current user
    """
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)

    post_service.downvote_post(post.id, current_user.id)
    return redirect(request.referrer)
