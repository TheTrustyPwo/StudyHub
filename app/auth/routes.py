from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.auth import auth_blueprint, auth_service
from app.auth.forms import RegisterForm, LoginForm


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    """
    Route for registering new users. On a GET request, it returns the registration
    form. On a POST request, it handles user registration.
    """
    if current_user.is_authenticated:
        return render_template("base.html")

    form = RegisterForm()
    if form.validate_on_submit():
        auth_service.register_user(form.email.data, form.username.data, form.password.data)
        flash("Successfully registered.", "primary")

        login_successful = auth_service.log_in_user(form.email.data, form.password.data)
        if login_successful:
            flash("Successfully logged in.", "primary")
            next_location = request.args.get("next")

            if next_location is None or not next_location.startswith("/"):
                return render_template("base.html")

            return redirect(next_location)

        flash("Login Failed", "danger")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """
    Route for logging in users. On a GET request, it returns the login form. On a POST
    request, it handles user login.
    """
    if current_user.is_authenticated:
        return render_template("base.html")

    form = LoginForm()
    if form.validate_on_submit():
        login_successful = auth_service.log_in_user(form.email.data, form.password.data)
        if login_successful:
            flash("Successfully logged in.", "primary")
            next_location = request.args.get("next")

            if next_location is None or not next_location.startswith("/"):
                return render_template("base.html")

            return redirect(next_location)

        flash("Login Failed", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html", form=form)


@auth_blueprint.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    Route for logging out current users.
    """
    auth_service.log_out_user()
    flash("Successfully logged out.", "primary")
    return redirect(url_for("auth.login"))
