from typing import Tuple

from flask import jsonify, Response


class APIException(Exception):
    """
    Custom exception class to wrap API errors
    Initialize the Exception with a code, message, and payload
    """

    def __init__(self, status_code, message=None, payload=None, prefix='exceptions', statsd=None):
        super(APIException, self).__init__(*((message,) if message else ()))
        self.status_code = status_code
        self.message = message
        self.payload = payload

        if statsd:
            key = '{}.{}'.format(prefix, status_code) if prefix else '{}'.format(status_code)
            statsd.incr(key)

    def to_dict(self) -> dict:
        """
        Convert Exception class to a Python dictionary
        """
        val = dict(self.payload or ())
        if self.message:
            val['message'] = self.message
        return val


def handle_api_exception(error: APIException) -> Tuple[Response, int]:
    return jsonify(error.to_dict()), error.status_code


class BadRequest(APIException):
    """
    A 400 Exception normally coming from request parameter validation
    """

    def __init__(self, **kwargs):
        super().__init__(400, **kwargs)


class Unauthorized(APIException):
    """
    A 401 Unauthorized error from bad authentication
    """

    def __init__(self, **kwargs):
        super().__init__(401, **kwargs)


class Forbidden(APIException):
    """
    A 403 Forbidden exception when a user doesn't have access to a resource
    """

    def __init__(self, **kwargs):
        super().__init__(403, **kwargs)


class NotFound(APIException):
    """
    A 404 typical exception when a resource can't be found in the database
    """

    def __init__(self, **kwargs):
        super().__init__(404, **kwargs)


class Conflict(APIException):
    """
    A 409 conflict when there's a conflict creating or updating a resource
    """

    def __init__(self, **kwargs):
        super().__init__(409, **kwargs)


class Gone(APIException):
    """
    A 410 gone when let clients know a resource previously existed but has been removed
    """

    def __init__(self, **kwargs):
        super().__init__(410, **kwargs)


class UnsupportedMedia(APIException):
    """
    A 415 indicates an invalid Accept or Content-Type header
    """

    def __init__(self, **kwargs):
        super().__init__(415, **kwargs)


class UnprocessableEntity(APIException):
    """
    A 422 POST or PUT means the parameters given can't be used
    """

    def __init__(self, **kwargs):
        super().__init__(422, **kwargs)


class FailedDependency(APIException):
    """
    A 424 Failed Dependency Exception.

    From httpstatuses.com:
    The method could not be performed on the resource because the requested
    action depended on another action and that action failed.
    """

    def __init__(self, **kwargs):
        super().__init__(424, **kwargs)
