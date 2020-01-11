import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.foursquare import FoursquareCheckinEvent


class FoursquareBackend(Backend):
    """
    This backend polls for new check-ins on the user's Foursquare account and triggers an event when a new check-in
    occurs.

    Requires:

        * The :class:`platypush.plugins.foursquare.FoursquarePlugin` plugin configured and enabled.

    Triggers:

        - :class:`platypush.message.event.foursquare.FoursquareCheckinEvent` when a new check-in occurs.

    """

    _last_created_at_varname = '_foursquare_checkin_last_created_at'

    def __init__(self, poll_seconds: float = 60.0, *args, **kwargs):
        """
        :param poll_seconds: How often the backend should check for new check-ins (default: one minute).
        """
        super().__init__(*args, **kwargs)
        self.poll_seconds = poll_seconds
        self._last_created_at = None

    def run(self):
        super().run()
        self._last_created_at = int(get_plugin('variable').get(self._last_created_at_varname).
                                    output.get(self._last_created_at_varname))
        self.logger.info('Started Foursquare backend')

        while not self.should_stop():
            try:
                checkins = get_plugin('foursquare').get_checkins().output
                if checkins:
                    last_checkin = checkins[0]
                    if not self._last_created_at or last_checkin.get('createdAt', 0) > self._last_created_at:
                        self.bus.post(FoursquareCheckinEvent(checkin=last_checkin))
                        self._last_created_at = last_checkin.get('createdAt', 0)
                        get_plugin('variable').set(**{self._last_created_at_varname: self._last_created_at})
            except Exception as e:
                self.logger.error('Error while retrieving the list of checkins: {}'.format(str(e)))
                self.logger.exception(e)
            finally:
                time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:
