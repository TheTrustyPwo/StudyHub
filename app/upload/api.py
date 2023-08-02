from flask import jsonify, request, render_template, redirect
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.upload import upload_api_blueprint, s3
from app.exceptions import Unauthorized, NotFound, BadRequest
from app.upload.files import File, FilePurpose


@upload_api_blueprint.route('/', methods=['POST'])
@login_required
def upload():
    purpose = request.args.get('purpose')
    if not purpose or not FilePurpose.has_key(purpose):
        raise BadRequest(message='Invalid file purpose')

    file_data = request.files['file']
    if not file_data:
        raise BadRequest(message='Upload must contain file')

    image = File(file_data, FilePurpose(purpose), current_user.id)
    url = image.upload()

    return jsonify({'url': url})


@upload_api_blueprint.route('view')
def view():
    return render_template('upload.html')
