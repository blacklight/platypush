import pytest
import requests

from .utils import (
    register_user,
    send_request as _send_request,
    test_pass,
    test_user,
)


@pytest.fixture(scope='module')
def expected_registration_redirect(base_url):
    yield f'{base_url}/auth?type=register&redirect={base_url}/execute'


@pytest.fixture(scope='module')
def expected_login_redirect(base_url):
    yield f'{base_url}/auth?type=login&redirect={base_url}/execute'


def send_request(**kwargs):
    return _send_request('shell.exec', args={'cmd': 'echo ping'}, **kwargs)


def test_request_with_no_registered_users(base_url, expected_registration_redirect):
    """
    An /execute request performed before any user is registered should redirect to the registration page.
    """
    response = send_request(authenticate=False, parse_json=False)
    if not (response.status_code == 412):
        raise AssertionError(
            'No users registered, but the execute endpoint returned '
            f'{response.status_code}'
        )


def test_first_user_registration(base_url):
    """
    Emulate a first user registration through form and get the session_token.
    """
    response = register_user()

    if not (
        response.json().get('status') == 'ok' and response.json().get('session_token')
    ):
        raise AssertionError('No session_token returned upon registration')


def _login(base_url):
    response = requests.post(
        f'{base_url}/auth?type=login&redirect=/',
        data={'username': test_user, 'password': test_pass},
    )
    response.raise_for_status()
    return response.json()


def test_login_returns_session_and_csrf_tokens(base_url):
    data = _login(base_url)
    if not (
        data.get('status') == 'ok'
        and data.get('session_token')
        and data.get('csrf_token')
    ):
        raise AssertionError('Login did not return both session and CSRF tokens')


def test_session_token_creation_with_csrf(base_url):
    login = _login(base_url)
    response = requests.post(
        f'{base_url}/auth?type=token',
        cookies={'session_token': login['session_token']},
        headers={'X-CSRF-Token': login['csrf_token']},
        json={'name': 'Test token', 'expiry_days': 1},
    )
    if not (response.status_code == 200 and response.json().get('token')):
        raise AssertionError('Session-mode token creation with valid CSRF failed')


def test_session_token_creation_without_csrf(base_url):
    login = _login(base_url)
    response = requests.post(
        f'{base_url}/auth?type=token',
        cookies={'session_token': login['session_token']},
        json={'name': 'Test token', 'expiry_days': 1},
    )
    if not (
        response.status_code == 403 and response.json().get('error') == 'INVALID_CSRF'
    ):
        raise AssertionError(
            f'Token creation without CSRF header should fail with INVALID_CSRF, '
            f'got {response.status_code}: {response.text}'
        )


def test_session_token_creation_with_wrong_csrf(base_url):
    login = _login(base_url)
    response = requests.post(
        f'{base_url}/auth?type=token',
        cookies={'session_token': login['session_token']},
        headers={'X-CSRF-Token': 'invalid-csrf-token'},
        json={'name': 'Test token', 'expiry_days': 1},
    )
    if not (
        response.status_code == 403 and response.json().get('error') == 'INVALID_CSRF'
    ):
        raise AssertionError(
            'Token creation with wrong CSRF should fail with INVALID_CSRF'
        )


def test_session_token_creation_with_invalid_session(base_url):
    response = requests.post(
        f'{base_url}/auth?type=token',
        cookies={'session_token': 'invalid-session-token'},
        headers={'X-CSRF-Token': 'any-token'},
        json={'name': 'Test token', 'expiry_days': 1},
    )
    data = response.json()
    if not (response.status_code == 401 and data.get('message') == 'Invalid session'):
        raise AssertionError(
            f'Token creation with invalid session should fail with an invalid session error, '
            f'got {response.status_code}: {response.text}'
        )


def test_credential_token_creation_without_2fa(base_url):
    response = requests.post(
        f'{base_url}/auth?type=token',
        json={
            'username': test_user,
            'password': test_pass,
            'name': 'Credential token',
            'expiry_days': 1,
        },
    )
    if not (response.status_code == 200 and response.json().get('token')):
        raise AssertionError('Credential-mode token creation without 2FA failed')


def test_session_token_creation_with_duplicate_name(base_url):
    login = _login(base_url)
    requests.post(
        f'{base_url}/auth?type=token',
        cookies={'session_token': login['session_token']},
        headers={'X-CSRF-Token': login['csrf_token']},
        json={'name': 'Duplicate token', 'expiry_days': 1},
    )

    response = requests.post(
        f'{base_url}/auth?type=token',
        cookies={'session_token': login['session_token']},
        headers={'X-CSRF-Token': login['csrf_token']},
        json={'name': 'Duplicate token', 'expiry_days': 1},
    )
    if not (
        response.status_code == 400
        and response.json().get('error') == 'TOKEN_NAME_EXISTS'
    ):
        raise AssertionError(
            f'Token creation with duplicate name should fail with TOKEN_NAME_EXISTS, '
            f'got {response.status_code}: {response.text}'
        )


def test_jwt_token_creation_without_2fa(base_url):
    response = requests.post(
        f'{base_url}/auth?type=jwt',
        json={
            'username': test_user,
            'password': test_pass,
            'expiry_days': 1,
        },
    )
    if not (response.status_code == 200 and response.json().get('token')):
        raise AssertionError(
            f'JWT token creation without 2FA failed: {response.status_code}: {response.text}'
        )


def test_jwt_token_creation_with_invalid_credentials(base_url):
    response = requests.post(
        f'{base_url}/auth?type=jwt',
        json={
            'username': test_user,
            'password': 'wrong-password',
            'expiry_days': 1,
        },
    )
    if not (
        response.status_code == 401
        and response.json().get('error') == 'INVALID_CREDENTIALS'
    ):
        raise AssertionError(
            f'JWT token creation with wrong password should fail with INVALID_CREDENTIALS, '
            f'got {response.status_code}: {response.text}'
        )


def test_unauthorized_request_with_registered_user(base_url, expected_login_redirect):
    """
    After a first user has been registered any unauthenticated call to /execute should redirect to /auth.
    """
    response = send_request(authenticate=False, parse_json=False)
    if not (response.status_code == 401):
        raise AssertionError(
            'An unauthenticated request after user registration should result in a '
            f'401 error, got {response.status_code} instead'
        )


def test_authorized_request_with_registered_user(base_url):
    # A request authenticated with user/pass should succeed.
    response = send_request(authenticate=True)
    if not (response.output.strip() == 'ping'):
        raise AssertionError('The request did not return the expected output')


def test_request_with_wrong_credentials(base_url, expected_login_redirect):
    # A request with the wrong user/pass should fail.
    response = send_request(
        authenticate=False, auth=('wrong', 'wrong'), parse_json=False
    )
    if not (response.status_code == 401):
        raise AssertionError(
            'A request with wrong credentials should fail with status 401, '
            f'got {response.status_code} instead'
        )


if __name__ == '__main__':
    pytest.main()


# vim:sw=4:ts=4:et:
