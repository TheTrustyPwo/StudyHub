import boto3
import os
from flask import Blueprint

session = boto3.Session()
s3 = session.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY', 'aws'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'aws'))

upload_api_blueprint = Blueprint('upload_api', __name__, url_prefix='/api/v1/upload')

from app.upload import api
