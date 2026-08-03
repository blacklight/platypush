"""
Tests for the PLATYPUSH_API_TOKEN environment variable authentication feature.

When the ``PLATYPUSH_API_TOKEN`` environment variable is set, Platypush should accept
requests that carry that token value (via X-Token header, Authorization Bearer,
or ``?token`` query parameter) without requiring a registered user or a DB
lookup.
"""

import os
from unittest.mock import patch

from platypush.backend.http.app.utils.auth import authenticate_token
from platypush.user import User

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ENV_TOKEN_VALUE = 'super-secret-env-token-1234'


class _FakeRequest:
    """Minimal request stub that `authenticate_token` can inspect."""

    def __init__(self, headers=None, args=None):
        self.headers = headers or {}
        self._args = args or {}

    # Flask-style args
    @property
    def args(self):
        return self._args


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def _auth_with_x_token(token: str):
    req = _FakeRequest(headers={'X-Token': token})
    return authenticate_token(req)


def _auth_with_bearer(token: str):
    req = _FakeRequest(headers={'Authorization': f'Bearer {token}'})
    return authenticate_token(req)


def _auth_with_query_param(token: str):
    req = _FakeRequest(args={'token': token})
    return authenticate_token(req)


class TestEnvTokenAuthentication:
    """Env-token authentication is accepted when PLATYPUSH_API_TOKEN is set."""

    def test_x_token_header_accepted(self):
        with patch.dict(os.environ, {'PLATYPUSH_API_TOKEN': ENV_TOKEN_VALUE}):
            user = _auth_with_x_token(ENV_TOKEN_VALUE)

        assert isinstance(user, User), 'Expected a User object for valid env token'
        assert user.username == '__env_token__'

    def test_bearer_authorization_accepted(self):
        with patch.dict(os.environ, {'PLATYPUSH_API_TOKEN': ENV_TOKEN_VALUE}):
            user = _auth_with_bearer(ENV_TOKEN_VALUE)

        assert isinstance(user, User), 'Expected a User object for valid env token'
        assert user.username == '__env_token__'

    def test_query_param_accepted(self):
        with patch.dict(os.environ, {'PLATYPUSH_API_TOKEN': ENV_TOKEN_VALUE}):
            user = _auth_with_query_param(ENV_TOKEN_VALUE)

        assert isinstance(user, User), 'Expected a User object for valid env token'
        assert user.username == '__env_token__'

    def test_wrong_token_rejected(self):
        with patch.dict(os.environ, {'PLATYPUSH_API_TOKEN': ENV_TOKEN_VALUE}):
            user = _auth_with_x_token('wrong-token')

        assert user is None, 'Expected None for wrong token value'

    def test_no_env_var_set(self):
        """Without PLATYPUSH_API_TOKEN set the env-token path is skipped entirely."""
        env = {k: v for k, v in os.environ.items() if k != 'PLATYPUSH_API_TOKEN'}
        with patch.dict(os.environ, env, clear=True):
            user = _auth_with_x_token(ENV_TOKEN_VALUE)

        assert user is None, 'Expected None when PLATYPUSH_API_TOKEN is not set'

    def test_empty_env_var_rejected(self):
        """An empty PLATYPUSH_API_TOKEN must not grant access."""
        with patch.dict(os.environ, {'PLATYPUSH_API_TOKEN': ''}):
            user = _auth_with_x_token('')

        assert user is None, 'Expected None for empty token value'
