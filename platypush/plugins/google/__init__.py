"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import os

from platypush.plugins import Plugin
from platypush.plugins.google.credentials import get_credentials


class GooglePlugin(Plugin):
    """
    Executes calls to the Google APIs using the google-api-python-client.
    This class is extended by ``GoogleMailPlugin``, ``GoogleCalendarPlugin`` etc.
    In order to use Google services (like GMail, Maps, Calendar etc.) with
    your account you need to:

        1. Create your Google application, if you don't have one already, on
        the developers console, https://console.developers.google.com

        2. Click on "Credentials", then "Create credentials" -> "OAuth client ID"

        3 Select "Other", enter whichever description you like, and create

        4. Click on the "Download JSON" icon next to your newly created client ID

        5. Generate a credentials file for the needed scope::

            python -m platypush.plugins.google.credentials 'https://www.googleapis.com/auth/gmail.compose' ~/client_secret.json

    Requires:

        * **google-api-python-client** (``pip install google-api-python-client``)
    """

    def __init__(self, scopes, *args, **kwargs):
        """
        Initialized the Google plugin with the required scopes.

        :param scopes: List of required scopes
        :type scopes: list
        """

        super().__init__(*args, **kwargs)
        self.credentials = {}

        for scope in scopes:
            self.credentials[scope] = get_credentials(scope)


# vim:sw=4:ts=4:et:

