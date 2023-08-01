from flask import render_template

from app.models import Post
from app.post import post_blueprint


@post_blueprint.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    return render_template("post.html", tab="recent")
