from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.feed import feed_blueprint, feed_service

@login_required
@feed_blueprint.route("/")
@feed_blueprint.route("/home")
def home():
    return render_template("home.html")
