from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.post import post_blueprint
from app.exceptions import Unauthorized, NotFound
from app.models import Post

@post_blueprint.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    return render_template("post.html", tab="recent")
