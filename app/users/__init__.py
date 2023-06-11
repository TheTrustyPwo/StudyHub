from flask import Blueprint

user_blueprint = Blueprint('user', __name__)
user_api_blueprint = Blueprint('user_api', __name__, url_prefix='/api/v1/users')

from app.users import routes, api
