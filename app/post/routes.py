import bleach
from flask import render_template, url_for, redirect
from flask_login import login_required, current_user

from app.models import Post, Subject
from app.post import post_blueprint
from app.post.forms import CreatePostForm
from app.upload.files import PostAttachment


@post_blueprint.route("/post/<int:post_id>")
@login_required
def view_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    return render_template("post.html", post=post)


@post_blueprint.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        title = bleach.clean(form.title.data)
        body = bleach.clean(form.body.data)
        subject = form.subject.data
        attachment = form.attachment.data

        filename = None
        if attachment:
            image = PostAttachment(attachment, current_user.id)
            image.upload()
            filename = image.filename

        post = Post(title=title, post=body, subject=Subject(subject), user_id=current_user.id, attachment_name=filename)
        post.save()

        return redirect(url_for('post.view_post', post_id=post.id))

    return render_template('create_post.html', form=form)
