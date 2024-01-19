from typing import Collection, Optional

from platypush.plugins import Plugin


class GooglePlugin(Plugin):
    """
    Integrates with the Google APIs using the google-api-python-client.

    This class is extended by ``GoogleMailPlugin``, ``GoogleCalendarPlugin`` etc.

    In order to use Google services (like GMail, Maps, Calendar etc.) with
    your account you need to:

        1. Create your Google application, if you don't have one already, on
           the `developers console <https://console.developers.google.com>`_.

        2. You may have to explicitly enable your user to use the app if the app
           is created in test mode. Go to "OAuth consent screen" and add your user's
           email address to the list of authorized users.

        3. Select the scopes that you want to enable for your application, depending
           on the integrations that you want to use.
           See https://developers.google.com/identity/protocols/oauth2/scopes
           for a list of the available scopes.

        4. Click on "Credentials", then "Create credentials" -> "OAuth client ID".

        5. Select "Desktop app", enter whichever name you like, and click "Create".

        6. Click on the "Download JSON" icon next to your newly created client ID.
           Save the JSON file under
           ``<WORKDIR>/credentials/google/client_secret.json``.

        7. If you're running the service on a desktop environment, then you
           can just start the application. A browser window will open and
           you'll be asked to authorize the application - you may be prompted
           with a warning because you are running a personal and potentially
           unverified application. After authorizing the application, the
           process will save the credentials under
           ``<WORKDIR>/credentials/google/<list,of,scopes>.json`` and proceed
           with the plugin initialization.

        8. If you're running the service on a headless environment, or you
           prefer to manually generate the credentials file before copying to
           another machine, you can run the following command:

               .. code-block:: bash

                  mkdir -p <WORKDIR>/credentials/google
                  python -m platypush.plugins.google.credentials \
                      'calendar.readonly,gmail.modify' \
                      <WORKDIR>/credentials/google/client_secret.json [--noauth_local_webserver]

           When launched with ``--noauth_local_webserver``, the script will
           start a local webserver and print a URL that should be opened in
           your browser. After authorizing the application, you may be
           prompted with a code that you should copy and paste back to the
           script. Otherwise, if you're running the script on a desktop, a
           browser window will be opened automatically.

    """

    def __init__(
        self,
        scopes: Optional[Collection[str]] = None,
        secrets_path: Optional[str] = None,
        **kwargs
    ):
        """
        :param scopes: List of scopes required by the API.
            See https://developers.google.com/identity/protocols/oauth2/scopes
            for a list of the available scopes. Override it in your configuration
            only if you need specific scopes that aren't normally required by the
            plugin.
        :param secrets_path: Path to the client secrets file.
            You can create your secrets.json from https://console.developers.google.com.
            Default: ``<PLATYPUSH_WORKDIR>/credentials/google/client_secret.json``.
        """

        from platypush.plugins.google.credentials import (
            get_credentials,
            default_secrets_file,
        )

        super().__init__(**kwargs)
        self._scopes = scopes or []
        self._secrets_path: str = secrets_path or default_secrets_file

        if self._scopes:
            scopes = " ".join(sorted(self._scopes))
            self.credentials = {
                scopes: get_credentials(scopes, secrets_file=self._secrets_path)
            }
        else:
            self.credentials = {}

    def get_service(
        self, service: str, version: str, scopes: Optional[Collection[str]] = None
    ):
        import httplib2
        from apiclient import discovery

        if scopes is None:
            scopes = getattr(self, "scopes", [])

        scopes = " ".join(sorted(scopes))
        credentials = self.credentials[scopes]
        http = credentials.authorize(httplib2.Http())
        return discovery.build(service, version, http=http, cache_discovery=False)


# vim:sw=4:ts=4:et:
