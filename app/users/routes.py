from app.models import User
from app.users import user_blueprint, user_service


@user_blueprint.route("/users/<string:username>")
def view_user(username: str):
    """
    Route displaying a user's profile page
    """
    user = User.query.filter_by(username=username).first_or_404()
    return user.username
    # return render_template("user.html", user=user)
