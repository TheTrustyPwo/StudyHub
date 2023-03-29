from app.models import User
from app.users import user_blueprint, service


@user_blueprint.route("/users/<string:username>")
def view_user(username: str):
    """
    Route displaying a user's profile page
    """
    user = User.get_by_username(username)
    return user.username
    # return render_template("user.html", user=user)
