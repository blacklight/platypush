import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.google.fit import GoogleFitEvent


class GoogleFitBackend(Backend):
    """
    This backend will listen for new Google Fit events (e.g. new weight/height
    measurements, new fitness activities etc.) on the specified data streams and
    fire an event upon new data.

    Triggers:

        * :class:`platypush.message.event.google.fit.GoogleFitEvent` when a new
            data point is received on one of the registered streams.

    Requires:

        * The **google.fit** plugin
            (:class:`platypush.plugins.google.fit.GoogleFitPlugin`) enabled.
        * The **db** plugin (:class:`platypush.plugins.db`) configured
    """

    _default_poll_seconds = 60
    _default_user_id = 'me'
    _last_timestamp_varname = '_GOOGLE_FIT_LAST_TIMESTAMP'

    def __init__(self, data_sources, user_id=_default_user_id,
                 poll_seconds=_default_poll_seconds, *args, **kwargs):
        """
        :param data_sources: Google Fit data source IDs to monitor. You can
            get a list of the available data sources through the
            :method:`platypush.plugins.google.fit.get_data_sources` action
        :type data_sources: list[str]

        :param user_id: Google user ID to track (default: 'me')
        :type user_id: str

        :param poll_seconds: How often the backend will query the data sources
            for new data points (default: 60 seconds)
        :type poll_seconds: float
        """

        super().__init__(*args, **kwargs)

        self.data_sources = data_sources
        self.user_id = user_id
        self.poll_seconds = poll_seconds


    def run(self):
        super().run()
        self.logger.info('Started Google Fit backend on data sources {}'.format(
            self.data_sources))

        while not self.should_stop():
            last_timestamp = float(get_plugin('variable').
                                   get(self._last_timestamp_varname).output.
                                   get(self._last_timestamp_varname)) or 0

            for data_source in self.data_sources:
                new_last_timestamp = last_timestamp

                for dp in get_plugin('google.fit').get_data(
                        user_id=self.user_id, data_source_id=data_source).output:
                    dp_time = dp.get('startTime', 0)
                    if  dp_time > last_timestamp:
                        self.bus.post(GoogleFitEvent(
                            user_id=self.user_id, data_source_id=data_source,
                            data_type=dp.get('dataTypeName'),
                            start_time=dp.get('startTime'),
                            end_time=dp.get('endTime'),
                            modified_time=dp.get('modifiedTime'),
                            values=dp.get('values')))

                        if dp_time > new_last_timestamp:
                            new_last_timestamp = dp_time

                last_timestamp = new_last_timestamp

            get_plugin('variable').set(**{
                self._last_timestamp_varname: last_timestamp})
            time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:
