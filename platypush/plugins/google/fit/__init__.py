from datetime import datetime
from typing import Generator, Iterable, Optional

from platypush.context import Variable
from platypush.message.event.google.fit import GoogleFitEvent
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.google import GooglePlugin
from platypush.utils import camel_case_to_snake_case


class GoogleFitPlugin(GooglePlugin, RunnablePlugin):
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

    When not configured with any ``data_sources``, the plugin won't start the
    event monitor and won't trigger any
    :class:`platypush.message.event.google.fit.GoogleFitEvent`. You can still
    fetch data points programmatically through the :meth:`.get_data` though.

    If you want to monitor data sources and fire events, then you need to
    explicitly define which health metrics you want to monitor through this
    integration.

    After starting the plugin, you can get a list of the available data sources
    by running the :meth:`.get_data_sources` action. The ``dataStreamId``
    fields are usually the ones you want to configure in your data sources.

    Unless you are interested in monitoring data points from specific devices,
    you may want to look for ``dataStreamId`` fields that match the
    ``derived:*:merge*`` pattern. Some popular examples include:e.g.

        - ``derived:com.google.step_count.delta:merge_step_deltas``, to monitor
          the number of steps taken in a given time interval.

        - ``derived:com.google.active_minutes:com.google.android.gms:merge_active_minutes``,
          to monitor the number of active minutes in a given time interval.

        - ``derived:com.google.speed:com.google.android.gms:merge_speed``, to
          monitor the speed in a given time interval.

        - ``derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended``,
          to monitor the number of calories burned in a given time interval.

        - ``derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm``,
          to monitor the heart rate measured in a given time interval.

    """

    scopes = [
        'https://www.googleapis.com/auth/fitness.activity.read',
        'https://www.googleapis.com/auth/fitness.body.read',
        'https://www.googleapis.com/auth/fitness.body_temperature.read',
        'https://www.googleapis.com/auth/fitness.heart_rate.read',
        'https://www.googleapis.com/auth/fitness.sleep.read',
        'https://www.googleapis.com/auth/fitness.location.read',
    ]

    _default_user_id = 'me'
    _last_timestamp_varname = '_GOOGLE_FIT_LAST_TIMESTAMP_'

    def __init__(
        self,
        data_sources: Iterable[str] = (),
        user_id: str = _default_user_id,
        poll_interval: float = 120.0,
        **kwargs,
    ):
        """
        :param data_sources: Google Fit data source IDs to monitor - e.g.
            weight, heartbeat, steps etc. You can get a list of the available
            data sources on your account through the :meth:`.get_data_sources`
            action. If none is specified then no sources will be monitored.
        :param user_id: Default Google user_id (default: 'me', default
            configured account user)
        :param poll_interval: How often the plugin should poll for new events
            (default: 120 seconds).
        """

        super().__init__(
            scopes=self.scopes,
            poll_interval=poll_interval,
            disable_monitor=not data_sources,
            **kwargs,
        )

        self.user_id = user_id
        self.data_sources = data_sources

    def _last_timestamp_var(self, data_source: str) -> Variable:
        return Variable(self._last_timestamp_varname + data_source)

    def _get_last_timestamp(self, data_source: str) -> float:
        return float(self._last_timestamp_var(data_source).get() or 0)

    def _set_last_timestamp(self, data_source: str, timestamp: float):
        self._last_timestamp_var(data_source).set(timestamp)

    @action
    def get_data_sources(self, user_id: Optional[str] = None):
        """
        Get the available data sources for the specified user.

        :param user_id: Target user ID (default: configured user).
        """
        from googleapiclient.errors import HttpError

        service = self.get_service(service='fitness', version='v1')

        try:
            sources = (
                service.users()  # pylint: disable=no-member
                .dataSources()
                .list(userId=user_id or self.user_id)
                .execute()
            )
        except HttpError as e:
            err = f'Error while getting data sources: {e.status_code}: {e.reason}'
            self.logger.warning(err)
            raise AssertionError(err) from e

        return sources['dataSource']

    @action
    def get_data(
        self,
        data_source_id: str,
        user_id: Optional[str] = None,
        limit: Optional[int] = 100,
    ):
        """
        Get raw data for the specified data_source_id

        :param data_source_id: Data source ID, see `get_data_sources`
        :type data_source_id: str
        :param user_id: Target user ID (default: configured user).
        :param limit: Maximum number of items to return.
        """
        return list(
            self._get_data(data_source_id=data_source_id, user_id=user_id, limit=limit)
        )

    def _get_timestamp(self, dp: dict, prefix: str) -> Optional[float]:
        basename = name = prefix + 'Time'
        t = dp.pop(name, None)
        if t is not None:
            return float(t)

        name = basename + 'Millis'
        t = dp.pop(name, None)
        if t is not None:
            return float(t) / 1e3

        name = basename + 'Nanos'
        t = dp.pop(name, None)
        if t is not None:
            return float(t) / 1e9

    def _get_data(
        self, data_source_id, user_id: Optional[str] = None, limit: Optional[int] = 100
    ) -> Generator[dict, None, None]:
        from googleapiclient.errors import HttpError

        service = self.get_service(service='fitness', version='v1')
        kwargs = {
            'dataSourceId': data_source_id,
            'userId': user_id or self.user_id,
        }

        if limit:
            kwargs['limit'] = limit

        try:
            for data_point in (
                service.users()  # pylint: disable=no-member
                .dataSources()
                .dataPointChanges()
                .list(**kwargs)
                .execute()
                .get('insertedDataPoint', [])
            ):
                data_point['startTime'] = self._get_timestamp(data_point, 'start')
                data_point['endTime'] = self._get_timestamp(data_point, 'end')
                data_point['modifiedTime'] = self._get_timestamp(data_point, 'modified')
                values = []

                for value in data_point.pop('value', data_point.pop('values', [])):
                    if isinstance(value, (int, float, str)):
                        values.append(value)
                        continue

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
                yield data_point
        except HttpError as e:
            err = f'Error while getting data points: {e.status_code}: {e.reason}'
            self.logger.warning(err)
            raise AssertionError(err) from e

    def _process_data_source(self, data_source: str):
        last_timestamp = new_last_timestamp = self._get_last_timestamp(data_source)

        self.logger.debug(
            'Processing new entries from data source %s, last timestamp: %s',
            data_source,
            datetime.fromtimestamp(last_timestamp).isoformat(),
        )

        new_data_points = 0
        for dp in self._get_data(
            user_id=self.user_id,
            data_source_id=data_source,
            limit=100,
        ):
            dp_time = dp.pop('startTime', 0)
            dp.pop('dataStreamId', None)

            if dp_time > last_timestamp:
                self._bus.post(
                    GoogleFitEvent(
                        user_id=self.user_id,
                        data_source_id=data_source,
                        data_type=dp.pop('dataTypeName'),
                        start_time=dp_time,
                        end_time=dp.pop('endTime'),
                        modified_time=dp.pop('modifiedTime'),
                        values=dp.pop('values'),
                        **{camel_case_to_snake_case(k): v for k, v in dp.items()},
                    )
                )

                new_data_points += 1

            new_last_timestamp = max(dp_time, new_last_timestamp)

        last_timestamp = new_last_timestamp
        if new_data_points > 0:
            self._set_last_timestamp(data_source, last_timestamp)
            self.logger.info(
                'Got %d new entries from data source %s, last timestamp: %s',
                new_data_points,
                data_source,
                datetime.fromtimestamp(last_timestamp).isoformat(),
            )

    def main(self):
        while not self.should_stop():
            try:
                for data_source in self.data_sources:
                    self._process_data_source(data_source)
            except Exception as e:
                self.logger.warning('Exception while processing Fit data')
                self.logger.exception(e)
            finally:
                self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
