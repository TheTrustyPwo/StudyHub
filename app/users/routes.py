from flask import render_template, abort

from app.models import User
from app.users import user_blueprint


@user_blueprint.route("/users/<string:username>")
def view_user(username: str):
    """
    Route displaying a user's profile page
    """
    user = User.get_by_username(username)
    if not user:
        abort(404)
    return render_template("user.html", user=user)
