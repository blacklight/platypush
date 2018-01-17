import os

from platypush.plugins import Plugin
from platypush.plugins.google.credentials import get_credentials


class GooglePlugin(Plugin):
    """
    Executes calls to the Google APIs using the google-api-python-client.
    In order to use Google services (like GMail, Maps, Calendar etc.) with
    your account you need to:

        1. Create your Google application, if you don't have one already, on
        the developers console, https://console.developers.google.com

        2. Click on "Credentials", then "Create credentials" -> "OAuth client ID"

        3 Select "Other", enter whichever description you like, and create

        4. Click on the "Download JSON" icon next to your newly created client ID

        5. Generate a credentials file for the needed scope:

            $ python -m platypush.plugins.google.credentials 'https://www.googleapis.com/auth/gmail.compose' ~/client_secret.json
    """

    def __init__(self, scopes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.credentials = {}

        for scope in scopes:
            self.credentials[scope] = get_credentials(scope)


# vim:sw=4:ts=4:et:

