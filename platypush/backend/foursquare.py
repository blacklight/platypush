from typing import Optional

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

    def __init__(self, poll_seconds: Optional[float] = 60.0, *args, **kwargs):
        """
        :param poll_seconds: How often the backend should check for new check-ins (default: one minute).
        """
        super().__init__(*args, poll_seconds=poll_seconds, **kwargs)
        self._last_created_at = None

    def __enter__(self):
        self._last_created_at = int(get_plugin('variable').get(self._last_created_at_varname).
                                    output.get(self._last_created_at_varname) or 0)
        self.logger.info('Started Foursquare backend')

    def loop(self):
        checkins = get_plugin('foursquare').get_checkins().output
        if not checkins:
            return

        last_checkin = checkins[0]
        last_checkin_created_at = last_checkin.get('createdAt', 0)
        if self._last_created_at and last_checkin_created_at <= self._last_created_at:
            return

        self.bus.post(FoursquareCheckinEvent(checkin=last_checkin))
        self._last_created_at = last_checkin_created_at
        get_plugin('variable').set(**{self._last_created_at_varname: self._last_created_at})


# vim:sw=4:ts=4:et:
