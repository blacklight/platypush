from platypush.plugins import action
from platypush.plugins.google import GooglePlugin


class GoogleFitPlugin(GooglePlugin):
    """
    Google Fit plugin.

    Requires:

        * **google-api-python-client** (``pip install google-api-python-client``)
        * **oauth2client** (``pip install oauth2client``)

    """

    scopes = ['https://www.googleapis.com/auth/fitness.activity.read',
              'https://www.googleapis.com/auth/fitness.body.read',
              'https://www.googleapis.com/auth/fitness.body_temperature.read',
              'https://www.googleapis.com/auth/fitness.heart_rate.read',
              'https://www.googleapis.com/auth/fitness.sleep.read',
              'https://www.googleapis.com/auth/fitness.location.read']

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
        sources = service.users().dataSources(). \
            list(userId=user_id or self.user_id).execute()

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

        for data_point in service.users().dataSources().dataPointChanges(). \
                list(**kwargs).execute().get('insertedDataPoint', []):
            data_point['startTime'] = float(data_point.pop('startTimeNanos'))/1e9
            data_point['endTime'] = float(data_point.pop('endTimeNanos'))/1e9
            data_point['modifiedTime'] = float(data_point.pop('modifiedTimeMillis'))/1e6
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
                            'intVal', v['value'].get(
                                'fpVal', v['value'].get('stringVal')))
                        for v in value['mapVal'] }

                values.append(value)

            data_point['values'] = values
            data_points.append(data_point)

        return data_points


# vim:sw=4:ts=4:et:
