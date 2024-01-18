from platypush.plugins import action
from platypush.plugins.google import GooglePlugin


class GoogleFitPlugin(GooglePlugin):
    r"""
    Google Fit plugin.

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

                  $ mkdir -p <WORKDIR>/credentials/google
                  $ roles="
                  fitness.activity.read,
                  fitness.body.read,
                  fitness.body_temperature.read,
                  fitness.heart_rate.read,
                  fitness.sleep.read,
                  fitness.location.read
                  "
                  $ python -m platypush.plugins.google.credentials "$roles" \
                      [--noauth_local_webserver] \
                      <WORKDIR>/credentials/google/client_secret.json

           When launched with ``--noauth_local_webserver``, the script will
           start a local webserver and print a URL that should be opened in
           your browser. After authorizing the application, you may be
           prompted with a code that you should copy and paste back to the
           script. Otherwise, if you're running the script on a desktop, a
           browser window will be opened automatically.

    """

    scopes = [
        'https://www.googleapis.com/auth/fitness.activity.read',
        'https://www.googleapis.com/auth/fitness.body.read',
        'https://www.googleapis.com/auth/fitness.body_temperature.read',
        'https://www.googleapis.com/auth/fitness.heart_rate.read',
        'https://www.googleapis.com/auth/fitness.sleep.read',
        'https://www.googleapis.com/auth/fitness.location.read',
    ]

    def __init__(self, user_id='me', *args, **kwargs):
        """
        :param user_id: Default Google user_id (default: 'me', default
            configured account user)
        :type user_id: str or int
        """

        super().__init__(scopes=self.scopes, *args, **kwargs)
        self.user_id = user_id

    @action
    def get_data_sources(self, user_id=None):
        """
        Get the available data sources for the specified user_id
        """

        service = self.get_service(service='fitness', version='v1')
        sources = (
            service.users().dataSources().list(userId=user_id or self.user_id).execute()
        )

        return sources['dataSource']

    @action
    def get_data(self, data_source_id, user_id=None, limit=None):
        """
        Get raw data for the specified data_source_id

        :param data_source_id: Data source ID, see `get_data_sources`
        :type data_source_id: str
        :param user_id: Target user ID (default: configured user).
        :param limit: Maximum number of items to return.
        """

        service = self.get_service(service='fitness', version='v1')
        kwargs = {
            'dataSourceId': data_source_id,
            'userId': user_id or self.user_id,
        }

        if limit:
            kwargs['limit'] = limit
        data_points = []

        for data_point in (
            service.users()
            .dataSources()
            .dataPointChanges()
            .list(**kwargs)
            .execute()
            .get('insertedDataPoint', [])
        ):
            data_point['startTime'] = float(data_point.pop('startTimeNanos')) / 1e9
            data_point['endTime'] = float(data_point.pop('endTimeNanos')) / 1e9
            data_point['modifiedTime'] = (
                float(data_point.pop('modifiedTimeMillis')) / 1e6
            )
            values = []

            for value in data_point.pop('value'):
                if value.get('intVal') is not None:
                    value = value['intVal']
                elif value.get('fpVal') is not None:
                    value = value['fpVal']
                elif value.get('stringVal') is not None:
                    value = value['stringVal']
                elif value.get('mapVal'):
                    value = {
                        v['key']: v['value'].get(
                            'intVal',
                            v['value'].get('fpVal', v['value'].get('stringVal')),
                        )
                        for v in value['mapVal']
                    }

                values.append(value)

            data_point['values'] = values
            data_points.append(data_point)

        return data_points


# vim:sw=4:ts=4:et:
