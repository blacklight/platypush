from typing import Optional

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.travisci import TravisciBuildPassedEvent, TravisciBuildFailedEvent


class TravisciBackend(Backend):
    """
    This backend polls for new builds on a `Travis-Ci <https://travis-ci.org>`_ account and triggers an event
    whenever a new build is completed.

    Requires:

        * The :class:`platypush.plugins.foursquare.FoursquarePlugin` plugin configured and enabled.

    Triggers:

        - :class:`platypush.message.event.foursquare.FoursquareCheckinEvent` when a new check-in occurs.

    """

    _last_build_finished_at_varname = '_travisci_last_build_finished_at'

    def __init__(self, poll_seconds: Optional[float] = 60.0, *args, **kwargs):
        """
        :param poll_seconds: How often the backend should check for new builds (default: one minute).
        """
        super().__init__(*args, poll_seconds=poll_seconds, **kwargs)
        self._last_build_finished_at = None

    def __enter__(self):
        self._last_build_finished_at = int(get_plugin('variable').get(self._last_build_finished_at_varname).
                                           output.get(self._last_build_finished_at_varname) or 0)
        self.logger.info('Started Travis-CI backend')

    def loop(self):
        builds = get_plugin('travisci').builds(limit=1).output
        if not builds:
            return

        last_build = builds[0]
        last_build_finished_at = last_build.get('finished_at', 0)
        if self._last_build_finished_at and last_build_finished_at <= self._last_build_finished_at:
            return

        if last_build.get('state') == 'passed':
            evt_type = TravisciBuildPassedEvent
        elif last_build.get('state') == 'failed':
            evt_type = TravisciBuildFailedEvent
        else:
            return

        evt = evt_type(repository_id=last_build.get('repository', {}).get('id'),
                       repository_name=last_build.get('repository', {}).get('name'),
                       repository_slug=last_build.get('repository').get('slug'),
                       build_id=int(last_build.get('id')),
                       build_number=int(last_build.get('number')),
                       duration=last_build.get('duration'),
                       previous_state=last_build.get('previous_state'),
                       private=last_build.get('private'),
                       tag=last_build.get('tag'),
                       branch=last_build.get('branch', {}).get('name'),
                       commit_id=last_build.get('commit', {}).get('id'),
                       commit_sha=last_build.get('commit', {}).get('sha'),
                       commit_message=last_build.get('commit', {}).get('message'),
                       committed_at=last_build.get('commit', {}).get('committed_at'),
                       created_by=last_build.get('created_by', {}).get('login'),
                       started_at=last_build.get('started_at'),
                       finished_at=last_build.get('finished_at'))

        self.bus.post(evt)
        self._last_build_finished_at = last_build_finished_at
        get_plugin('variable').set(**{self._last_build_finished_at_varname: self._last_build_finished_at})


# vim:sw=4:ts=4:et:
