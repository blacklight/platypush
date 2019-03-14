from apiclient import discovery

from platypush.plugins import action
from platypush.plugins.google import GooglePlugin


class GoogleFitPlugin(GooglePlugin):
    """
    Google Fit plugin
    """

    scopes = ['https://www.googleapis.com/auth/fitness.activity.read',
              'https://www.googleapis.com/auth/fitness.body.read',
              'https://www.googleapis.com/auth/fitness.body_temperature.read',
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
    def get_data(self, data_source_id, user_id=None):
        """
        Get raw data for the specified data_source_id

        :param data_source_id: Data source ID, see `get_data_sources`
        :type data_source_id: str
        """

        service = self.get_service(service='fitness', version='v1')
        return service.users().dataSources().dataPointChanges() \
            .list(dataSourceId=data_source_id, userId=user_id or self.user_id) \
            .execute().get('insertedDataPoint', [])


# vim:sw=4:ts=4:et:
