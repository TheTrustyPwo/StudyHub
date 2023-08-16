from typing import Type

import pinecone
from flask import Flask, render_template
from flask_cors import CORS
from flask_login import LoginManager
from flask_moment import Moment
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_talisman import Talisman

from oauthlib.oauth2 import WebApplicationClient

from app.config import BaseConfig, DevelopmentConfig

db = SQLAlchemy()
socketio = SocketIO()
moment = Moment()
cors = CORS()
migrate = Migrate()
talisman = Talisman()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "danger"

oauth_client = None


def create_app(config: Type[BaseConfig] = DevelopmentConfig):
    """
    Factory method for creating the Flask app.
    https://flask.palletsprojects.com/en/2.2.x/patterns/appfactories/
    """
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    socketio.init_app(app)
    moment.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    talisman.init_app(app, content_security_policy=[])
    login_manager.init_app(app)

    load_oauth_client(app)
    load_pinecone_index(app)

    from app.upload import upload_api_blueprint
    from app.auth import auth_blueprint
    from app.post import post_blueprint, post_api_blueprint
    from app.feed import feed_blueprint
    from app.replies import reply_blueprint, reply_api_blueprint
    from app.messages import messages_blueprint, messages_api_blueprint
    from app.conversations import conversations_blueprint, conversations_api_blueprint
    from app.users import user_blueprint, user_api_blueprint
    from app.ai import ai_blueprint, ai_api_blueprint

    app.register_blueprint(upload_api_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(post_blueprint)
    app.register_blueprint(post_api_blueprint)
    app.register_blueprint(feed_blueprint)
    app.register_blueprint(reply_blueprint)
    app.register_blueprint(reply_api_blueprint)
    app.register_blueprint(messages_blueprint)
    app.register_blueprint(messages_api_blueprint)
    app.register_blueprint(conversations_blueprint)
    app.register_blueprint(conversations_api_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(user_api_blueprint)
    app.register_blueprint(ai_blueprint)
    app.register_blueprint(ai_api_blueprint)

    from app.exceptions.api_exception import APIException, handle_api_exception
    app.register_error_handler(APIException, handle_api_exception)
    app.register_error_handler(404, lambda _: render_template('404.html'))

    with app.app_context():
        db.create_all()

    return app

def load_oauth_client(app):
    global oauth_client
    oauth_client = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])

def load_pinecone_index(app):
    pinecone.init(api_key=app.config['PINECONE_API_KEY'], environment=app.config['PINECONE_ENV'])
