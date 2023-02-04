import datetime
import jwt

from app import app, db, bcrypt

AUTH_TOKEN_EXPIRY_DAYS = app.config.get('AUTH_TOKEN_EXPIRY_DAYS')
AUTH_TOKEN_EXPIRY_SECONDS = app.config.get('AUTH_TOKEN_EXPIRY_SECONDS')
JWT_SIGNATURE_ALGORITHM = app.config.get('JWT_SIGNATURE_ALGORITHM')
BCRYPT_HASH_PREFIX = app.config.get('BCRYPT_HASH_PREFIX')
SECRET_KEY = app.config.get('SECRET_KEY')

print(AUTH_TOKEN_EXPIRY_DAYS, AUTH_TOKEN_EXPIRY_SECONDS)

class User(db.Model):
    """
    Table schema
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = bcrypt.generate_password_hash(password, rounds=BCRYPT_HASH_PREFIX, prefix=b'2b').decode('utf-8')
        self.registered_on = datetime.datetime.now()

    def save(self):
        """
        Persist the user in the database
        :return:
        """
        db.session.add(self)
        db.session.commit()
        return self.encode_auth_token(self.id)

    @staticmethod
    def encode_auth_token(user_id):
        """
        Encode the Auth token
        :param user_id: User's ID
        :return:
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=AUTH_TOKEN_EXPIRY_DAYS, seconds=AUTH_TOKEN_EXPIRY_SECONDS),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(payload, SECRET_KEY, algorithm=JWT_SIGNATURE_ALGORITHM)
        except Exception as ex:
            return ex

    @staticmethod
    def decode_auth_token(token):
        """
        Decoding the token to get the payload and then return the user ID in 'sub'
        :param token: Auth Token
        :return:
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=JWT_SIGNATURE_ALGORITHM)
            is_token_blacklisted = BlackListToken.check_blacklist(token)
            if is_token_blacklisted:
                return 'Token was Blacklisted, Please login In'
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired, Please sign in again'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please sign in again'

    @staticmethod
    def get_by_id(user_id):
        """
        Filter a user by Id.
        :param user_id:
        :return: User or None
        """
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_by_email(email):
        """
        Check a user by their email address
        :param email:
        :return:
        """
        return User.query.filter_by(email=email).first()

    def reset_password(self, new_password):
        """
        Update/reset the user password.
        :param new_password: New User Password
        :return:
        """
        self.password = bcrypt.generate_password_hash(new_password, rounds=BCRYPT_HASH_PREFIX, prefix=b'2b').decode('utf-8')
        db.session.commit()

class BlackListToken(db.Model):
    """
    Table to store blacklisted/invalid auth tokens
    """
    __tablename__ = 'blacklist_token'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def blacklist(self):
        """
        Persist Blacklisted token in the database
        :return:
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def check_blacklist(token):
        """
        Check to find out whether a token has already been blacklisted.
        :param token: Authorization token
        :return:
        """
        response = BlackListToken.query.filter_by(token=token).first()
        return bool(response)
