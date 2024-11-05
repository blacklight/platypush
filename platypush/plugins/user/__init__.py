from typing import List, Dict, Any, Optional, Tuple, Union

from platypush.plugins import Plugin, action
from platypush.user import UserManager


class UserPlugin(Plugin):
    """
    Plugin to programmatically create and manage users and user sessions
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_manager = UserManager()

    @action
    def create_user(
        self,
        username,
        password,
        executing_user=None,
        executing_user_password=None,
        session_token=None,
        **kwargs,
    ):
        """
        Create a user. This action needs to be executed by an already existing
        user, who needs to authenticate with their own credentials, unless this
        is the first user created on the system.

        :return:

            .. code-block:: json

                {
                    "user_id": 1,
                    "username": "test-user",
                    "created_at": "2020-11-26T22:41:40.550574"
                }

        """

        if (
            self.user_manager.get_user_count() > 0
            and not executing_user
            and not session_token
        ):
            return None, "You need to authenticate in order to create another user"

        if not self.user_manager.authenticate_user(
            executing_user, executing_user_password
        ):
            user, _ = self.user_manager.authenticate_user_session(session_token)[:2]
            if not user:
                return None, "Invalid credentials and/or session_token"

        try:
            user = self.user_manager.create_user(username, password, **kwargs)
        except (NameError, ValueError) as e:
            return None, str(e)

        return {
            'user_id': user.user_id,
            'username': user.username,
            'created_at': user.created_at.isoformat(),
        }

    @action
    def authenticate_user(
        self,
        username: str,
        password: str,
        code: Optional[str] = None,
        return_details: bool = False,
    ) -> Union[bool, Tuple[bool, str]]:
        """
        Authenticate a user.

        :param username: Username.
        :param password: Password.
        :param code: Optional 2FA code, if 2FA is enabled for the user.
        :param return_details: If True then return the error details in
            case of authentication failure.
        :return: If ``return_details`` is False (default), the action returns
            True if the provided credentials are valid, False otherwise.
            If ``return_details`` is True then the action returns a tuple
            (authenticated, error_details) where ``authenticated`` is True if
            the provided credentials are valid, False otherwise, and
            ``error_details`` is a string containing the error details in case
            of authentication failure. Supported error details are:

                - ``invalid_credentials``: Invalid username or password.
                - ``invalid_otp_code``: Invalid 2FA code.
                - ``missing_otp_code``: Username/password are correct, but a 2FA
                  code is required for the user.

        """
        response = self.user_manager.authenticate_user(
            username, password, code=code, with_status=return_details
        )

        if return_details:
            assert (
                isinstance(response, tuple) and len(response) == 2
            ), 'Invalid response from authenticate_user'
            return response[0], response[1].value

        return response

    @action
    def update_password(self, username, old_password, new_password):
        """
        Update the password of a user.

        :return: True if the password was successfully updated, false otherwise
        """

        return self.user_manager.update_password(username, old_password, new_password)

    @action
    def delete_user(
        self,
        username,
        executing_user=None,
        executing_user_password=None,
        session_token=None,
    ):
        """
        Delete a user.
        """

        if not self.user_manager.authenticate_user(
            executing_user, executing_user_password
        ):
            user, _ = self.user_manager.authenticate_user_session(session_token)[:2]
            if not user:
                return None, "Invalid credentials and/or session_token"

        try:
            return self.user_manager.delete_user(username)
        except NameError:
            return None, f"No such user: {username}"

    @action
    def create_session(self, username, password, code=None, expires_at=None):
        """
        Create a user session.

        :return:

            .. code-block:: json

                {
                    "session_token": "secret",
                    "user_id": 1,
                    "username": "test-user",
                    "created_at": "2020-11-26T22:41:40.550574",
                    "expires_at": "2020-11-26T22:41:40.550574"
                }

        """

        session = self.user_manager.create_user_session(
            username=username, password=password, code=code, expires_at=expires_at
        )

        if isinstance(session, tuple):
            session = session[0]

        if not session:
            return None, "Invalid credentials"

        return {
            'session_token': session.session_token,
            'user_id': session.user_id,
            'created_at': session.created_at.isoformat(),
            'expires_at': (
                session.expires_at.isoformat() if session.expires_at else None  # type: ignore
            ),
        }

    @action
    def authenticate_session(self, session_token):
        """
        Authenticate a session by token and return the associated user.

        :return:

            .. code-block:: json

                {
                    "user_id": 1,
                    "username": "test-user",
                    "created_at": "2020-11-26T22:41:40.550574"
                }

        """

        user, _ = self.user_manager.authenticate_user_session(session_token)[:2]
        if not user:
            return None, 'Invalid session token'

        return {
            'user_id': user.user_id,
            'username': user.username,
            'created_at': user.created_at.isoformat(),
        }

    @action
    def delete_session(self, session_token):
        """
        Delete a user session.
        """

        return self.user_manager.delete_user_session(session_token)

    @action
    def get_users(self) -> List[Dict[str, Any]]:
        """
        Get the list of registered users.

        :return:

            .. code-block:: json

                [
                    {
                        "user_id": 1,
                        "username": "user1",
                        "created_at": "2020-11-26T22:41:40.550574"
                    },
                    {
                        "user_id": 2,
                        "username": "user2",
                        "created_at": "2020-11-28T21:10:23.224813"
                    }
                ]

        """
        users = self.user_manager.get_users()
        return [
            {
                'user_id': user.user_id,
                'username': user.username,
                'created_at': user.created_at.isoformat(),
            }
            for user in users
        ]

    @action
    def get_user_by_session(self, session_token: str) -> dict:
        """
        Get the user record associated to a session token.

        :param session_token: Session token.
        :return:

            .. code-block:: json

                [
                    {
                        "user_id": 1,
                        "username": "user1",
                        "created_at": "2020-11-26T22:41:40.550574"
                    }
                ]

        """
        user = self.user_manager.get_user_by_session(session_token)
        assert user, 'No user associated with the specified session token'

        return {
            'user_id': user.user_id,
            'username': user.username,
            'created_at': user.created_at.isoformat(),
        }


# vim:sw=4:ts=4:et:
