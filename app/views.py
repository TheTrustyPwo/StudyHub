from flask import jsonify, make_response

from app import app


def response(status, message, status_code):
    """
    Make an http response helper
    :param status: Status message
    :param message: Response Message
    :param status_code: Http response code
    :return:
    """
    return make_response(jsonify({'status': status, 'message': message})), status_code


@app.errorhandler(404)
def route_not_found(e):
    """
    Return a custom 404 Http response message for missing or not found routes.
    :param e: Exception
    :return: Http Response
    """
    return response('failed', 'Endpoint not found', 404)


@app.errorhandler(405)
def method_not_found(e):
    """
    Custom response for methods not allowed for the requested URLs
    :param e: Exception
    :return:
    """
    return response('failed', 'The method is not allowed for the requested URL', 405)


@app.errorhandler(500)
def internal_server_error(e):
    """
    Return a custom message for a 500 internal error
    :param e: Exception
    :return:
    """
    return response('failed', 'Internal server error', 500)
