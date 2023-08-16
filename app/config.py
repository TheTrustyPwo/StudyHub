import os

base_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """
    Base application configuration
    """
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'strong_key')
    JSONIFY_PRETTYPRINT_REGULAR = True

    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ENV = 'gcp-starter'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///test.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CONTENT_SECURITY_POLICY = {
        'default-src': [
            "'self'",
            "https://code.jquery.com",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://thepwo.s3.amazonaws.com",
            "https://fonts.googleapis.com"
        ],
        'img-src': [
            '*',
            'data:'
        ],
        'style-src': [
            "'self'",
            "https://code.jquery.com",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://fonts.googleapis.com"
        ],
        'script-src': [
            "'self'",
            "https://code.jquery.com",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com"
        ],
        'font-src': '*'
    }


class DevelopmentConfig(BaseConfig):
    """
    Development application configuration
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///test.sqlite')


class TestingConfig(BaseConfig):
    """
    Testing application configuration
    """
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL_TEST', 'sqlite:///testt.sqlite')
    WTF_CSRF_ENABLED = False
