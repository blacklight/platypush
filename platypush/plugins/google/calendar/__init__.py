from platypush.plugins import action
from platypush.plugins.google import GooglePlugin
from platypush.plugins.calendar import CalendarInterface
from platypush.utils import utcnow


class GoogleCalendarPlugin(GooglePlugin, CalendarInterface):
    r"""
    Google Calendar plugin.

    In order to use this plugin:

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
                      'calendar.readonly' \
                      <WORKDIR>/credentials/google/client_secret.json [--noauth_local_webserver]

           When launched with ``--noauth_local_webserver``, the script will
           start a local webserver and print a URL that should be opened in
           your browser. After authorizing the application, you may be
           prompted with a code that you should copy and paste back to the
           script. Otherwise, if you're running the script on a desktop, a
           browser window will be opened automatically.

    """

    scopes = ['calendar.readonly']

    def __init__(self, *args, **kwargs):
        super().__init__(scopes=self.scopes, *args, **kwargs)

    @action
    def get_upcoming_events(self, max_results=10):
        """
        Get the upcoming events. See
        :meth:`platypush.plugins.calendar.CalendarPlugin.get_upcoming_events`.
        """

        now = utcnow().replace(tzinfo=None).isoformat() + 'Z'
        service = self.get_service('calendar', 'v3')
        result = (
            service.events()
            .list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime',
            )
            .execute()
        )

        events = result.get('items', [])
        return events


# vim:sw=4:ts=4:et:
