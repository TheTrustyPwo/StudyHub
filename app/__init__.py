from typing import Type

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_moment import Moment
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from app.config import BaseConfig, DevelopmentConfig

db = SQLAlchemy()
socketio = SocketIO()
moment = Moment()
cors = CORS()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "danger"


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
    login_manager.init_app(app)

    from app.auth import auth_blueprint
    from app.post import post_blueprint
    from app.feed import feed_blueprint
    from app.replies import reply_blueprint
    from app.messages import messages_blueprint, messages_api_blueprint
    from app.conversations import conversations_blueprint, conversations_api_blueprint
    from app.users import user_blueprint, user_api_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(post_blueprint)
    app.register_blueprint(feed_blueprint)
    app.register_blueprint(reply_blueprint)
    app.register_blueprint(messages_blueprint)
    app.register_blueprint(messages_api_blueprint)
    app.register_blueprint(conversations_blueprint)
    app.register_blueprint(conversations_api_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(user_api_blueprint)

    from app.exceptions.api_exception import APIException, handle_api_exception
    app.register_error_handler(APIException, handle_api_exception)

    with app.app_context():
        db.create_all()

    return app
