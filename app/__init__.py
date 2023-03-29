import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Initialize application
app = Flask(__name__)

# Enabling cors
CORS(app)

# app configuration
app_settings = os.getenv('APP_SETTINGS', 'app.config.DevelopmentConfig')
app.config.from_object(app_settings)

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# Initialize Flask Sql Alchemy
db = SQLAlchemy(app)

# Initialize Login Manager
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "danger"


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


from app.auth import auth_blueprint
from app.post import post_blueprint
from app.docs.docs import docs

app.register_blueprint(auth_blueprint)
app.register_blueprint(post_blueprint)
app.register_blueprint(docs)

with app.app_context():
    db.create_all()
