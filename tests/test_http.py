import pytest

from .utils import register_user, send_request as _send_request


@pytest.fixture(scope='module')
def expected_registration_redirect(base_url):
    yield '{base_url}/register?redirect={base_url}/execute'.format(base_url=base_url)


@pytest.fixture(scope='module')
def expected_login_redirect(base_url):
    yield '{base_url}/login?redirect={base_url}/execute'.format(base_url=base_url)


def send_request(**kwargs):
    return _send_request('shell.exec', args={'cmd': 'echo ping'}, **kwargs)


def test_request_with_no_registered_users(base_url, expected_registration_redirect):
    """
    An /execute request performed before any user is registered should redirect to the registration page.
    """
    response = send_request(authenticate=False, parse_json=False)
    assert response.status_code == 412, (
        'No users registered, but the execute endpoint returned '
        f'{response.status_code}'
    )


def test_first_user_registration(base_url):
    """
    Emulate a first user registration through form and get the session_token.
    """
    response = register_user()

    assert len(response.history) > 0, 'Redirect missing from the history'
    assert (
        'session_token' in response.history[0].cookies
    ), 'No session_token returned upon registration'
    assert (
        '{base_url}/'.format(base_url=base_url) == response.url
    ), 'The registration form did not redirect to the main panel'


def test_unauthorized_request_with_registered_user(base_url, expected_login_redirect):
    """
    After a first user has been registered any unauthenticated call to /execute should redirect to /login.
    """
    response = send_request(authenticate=False, parse_json=False)
    assert response.status_code == 401, (
        'An unauthenticated request after user registration should result in a '
        f'401 error, got {response.status_code} instead'
    )


def test_authorized_request_with_registered_user(base_url):
    # A request authenticated with user/pass should succeed.
    response = send_request(authenticate=True)
    assert (
        response.output.strip() == 'ping'
    ), 'The request did not return the expected output'


def test_request_with_wrong_credentials(base_url, expected_login_redirect):
    # A request with the wrong user/pass should fail.
    response = send_request(
        authenticate=False, auth=('wrong', 'wrong'), parse_json=False
    )
    assert response.status_code == 401, (
        'A request with wrong credentials should fail with status 401, '
        f'got {response.status_code} instead'
    )


if __name__ == '__main__':
    pytest.main()


# vim:sw=4:ts=4:et:
