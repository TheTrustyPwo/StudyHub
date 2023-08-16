from flask import flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_required, login_user
import requests

from app import oauth_client
from app.auth import auth_blueprint, auth_service
from app.auth.forms import RegisterForm, LoginForm
from app.models import User


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    """
    Route for registering new users.

    On a GET request, it returns the registration form.
    On a POST request, it handles user registration.
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
                return redirect(url_for('feed.home'))

            return redirect(next_location)

        flash("Login Failed", "danger")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """
    Route for logging in users.

    On a GET request, it returns the login form.
    On a POST request, it handles user login.
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
                return redirect(url_for('feed.home'))

            return redirect(next_location)

        flash("Login Failed", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html", form=form)


@auth_blueprint.route("/login/google")
def login_google():
    google_provider_cfg = auth_service.get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = oauth_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@auth_blueprint.route("/login/google/callback")
def login_google_callback():
    code = request.args.get("code")

    google_provider_cfg = auth_service.get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = oauth_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
    )

    oauth_client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = oauth_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if not userinfo_response.json().get("email_verified"):
        flash("Login Failed: Email not verified", "danger")
        return redirect(url_for("auth.login"))

    email = userinfo_response.json()["email"]
    picture = userinfo_response.json()["picture"]
    username = userinfo_response.json()["given_name"]

    user = User.get_by_email(email)
    if not user:
        user = User(email=email, username=username, password=None)
        user.save()

    login_user(user)

    return redirect(url_for('feed.home'))


@auth_blueprint.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    Route for logging out current users.
    """
    auth_service.log_out_user()
    flash("Successfully logged out.", "primary")
    return redirect(url_for("auth.login"))
