import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialize application
app = Flask(__name__, static_folder=None)

# Enabling cors
CORS(app)

# app configuration
app_settings = os.getenv('APP_SETTINGS', 'app.config.DevelopmentConfig')
app.config.from_object(app_settings)

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# Initialize Flask Sql Alchemy
db = SQLAlchemy(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


from app.users.auth import auth

app.register_blueprint(auth, url_prefix='/v1')

with app.app_context():
    db.create_all()
