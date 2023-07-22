from platypush.plugins import Plugin


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

            python -m platypush.plugins.google.credentials \
                'https://www.googleapis.com/auth/gmail.compose' ~/client_secret.json

    Requires:

        * **google-api-python-client** (``pip install google-api-python-client``)
        * **oauth2client** (``pip install oauth2client``)

    """

    def __init__(self, scopes=None, **kwargs):
        """
        Initialized the Google plugin with the required scopes.

        :param scopes: List of required scopes
        :type scopes: list
        """

        from platypush.plugins.google.credentials import get_credentials

        super().__init__(**kwargs)
        self._scopes = scopes or []

        if self._scopes:
            scopes = ' '.join(sorted(self._scopes))
            self.credentials = {scopes: get_credentials(scopes)}
        else:
            self.credentials = {}

    def get_service(self, service, version, scopes=None):
        import httplib2
        from apiclient import discovery

        if scopes is None:
            scopes = getattr(self, 'scopes', [])

        scopes = ' '.join(sorted(scopes))
        credentials = self.credentials[scopes]
        http = credentials.authorize(httplib2.Http())
        return discovery.build(service, version, http=http, cache_discovery=False)


# vim:sw=4:ts=4:et:
