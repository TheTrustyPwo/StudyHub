from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.post import post_blueprint, service
from app.models import Post
from app.post.forms import PostForm, UpdatePostForm

@post_blueprint.route("/post/<int:post_id>")
def view_post(post_id):
    """
    Route for page displaying a post and its replies sorted by date created.
    """
    page = int(request.args.get("page", 1))
    post = Post.get_by_id(post_id)
    if post:
        # replies = post_service.get_post_replies(post.id, page, False)
        return render_template("post.html", tab="recent", post=post)
    else:
        abort(404)

@post_blueprint.route("/post/create", methods=["GET", "POST"])
@login_required
def create_post():
    """
    Route for creating a post. On a GET request, it returns the post creation form. On
    a POST request, it handles creating a post.
    """
    form = PostForm()
    if form.validate_on_submit():
        post_id = service.create_post(form.title.data, form.post.data, current_user.id)
        flash("Successfully created post", "primary")
        return redirect(url_for("post.view_post", post_id=post_id))
    return render_template("create_post.html", form=form)
