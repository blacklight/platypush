import datetime
import json
import logging

from flask import Blueprint, request, abort, jsonify

from platypush.exceptions.user import UserException
from platypush.user import UserManager

auth = Blueprint('auth', __name__)
log = logging.getLogger(__name__)

# Declare routes list
__routes__ = [
    auth,
]


@auth.route('/auth', methods=['POST'])
def auth_endpoint():
    """
    Authentication endpoint. It validates the user credentials provided over a JSON payload with the following
    structure:

        .. code-block:: json

            {
                "username": "USERNAME",
                "password": "PASSWORD",
                "expiry_days": "The generated token should be valid for these many days"
            }

    ``expiry_days`` is optional, and if omitted or set to zero the token will be valid indefinitely.

    Upon successful validation, a new JWT token will be generated using the service's self-generated RSA key-pair and it
    will be returned to the user. The token can then be used to authenticate API calls to ``/execute`` by setting the
    ``Authorization: Bearer <TOKEN_HERE>`` header upon HTTP calls.

    :return: Return structure:

        .. code-block:: json

            {
                "token": "<generated token here>"
            }
    """
    try:
        payload = json.loads(request.get_data(as_text=True))
        username, password = payload['username'], payload['password']
    except Exception as e:
        log.warning('Invalid payload passed to the auth endpoint: ' + str(e))
        abort(400)

    expiry_days = payload.get('expiry_days')
    expires_at = None
    if expiry_days:
        expires_at = datetime.datetime.now() + datetime.timedelta(days=expiry_days)

    user_manager = UserManager()

    try:
        return jsonify({
            'token': user_manager.generate_jwt_token(username=username, password=password, expires_at=expires_at),
        })
    except UserException as e:
        abort(401, str(e))
