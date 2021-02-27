import os
import unittest

from . import BaseHttpTest, conf_dir


class TestHttp(BaseHttpTest):
    """
    Tests the full flow of a request/response on the HTTP backend.
    Runs a remote command over HTTP via shell.exec plugin and gets the output.
    """

    config_file = os.path.join(conf_dir, 'test_http_config.yaml')

    def __init__(self, *args, **kwargs):
        super(TestHttp, self).__init__(*args, **kwargs)

    def test_http_flow(self):
        # An /execute request performed before any user is registered should redirect to the registration page.
        expected_registration_redirect = '{base_url}/register?redirect={base_url}/execute'.format(
            base_url=self.base_url)
        expected_login_redirect = '{base_url}/login?redirect={base_url}/execute'.format(
            base_url=self.base_url)

        response = self.send_request(authenticate=False, parse_response=False)
        self.assertEqual(expected_registration_redirect, response.url,
                         'No users registered, but the application did not redirect us to the registration page')

        # Emulate a first user registration through form and get the session_token.
        response = self.register_user()
        self.assertGreater(len(response.history), 0, 'Redirect missing from the history')
        self.assertTrue('session_token' in response.history[0].cookies, 'No session_token returned upon registration')
        self.assertEqual('{base_url}/'.format(base_url=self.base_url), response.url,
                         'The registration form did not redirect to the main panel')

        # After a first user has been registered any unauthenticated call to /execute should redirect to /login.
        response = self.send_request(authenticate=False, parse_response=False)
        self.assertEqual(expected_login_redirect, response.url,
                         'An unauthenticated request after user registration should result in a login redirect')

        # A request authenticated with user/pass should succeed.
        response = self.send_request(authenticate=True)
        self.assertEqual(response.output.strip(), 'ping', 'The request did not return the expected output')

        # A request with the wrong user/pass should fail.
        response = self.send_request(authenticate=False, auth=('wrong', 'wrong'), parse_response=False)
        self.assertEqual(expected_login_redirect, response.url, 'A request with wrong credentials should fail')

    def send_request(self, **kwargs):
        return super().send_request('shell.exec', args={'cmd': 'echo ping'}, **kwargs)


if __name__ == '__main__':
    unittest.main()


# vim:sw=4:ts=4:et:
