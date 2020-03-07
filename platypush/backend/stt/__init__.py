import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.plugins.stt import SttPlugin


class SttBackend(Backend):
    """
    Base class for speech-to-text backends.
    """

    def __init__(self, plugin_name: str, retry_sleep: float = 5.0, *args, **kwargs):
        """
        :param plugin_name: Plugin name of the class that will be used for speech detection. Must be an instance of
            :class:`platypush.plugins.stt.SttPlugin`.
        :param retry_sleep: Number of seconds the backend will wait on failure before re-initializing the plugin
            (default: 5 seconds).
        """
        super().__init__(*args, **kwargs)
        self.plugin_name = plugin_name
        self.retry_sleep = retry_sleep

    def run(self):
        super().run()
        self.logger.info('Starting {} speech-to-text backend'.format(self.__class__.__name__))

        while not self.should_stop():
            try:
                plugin: SttPlugin = get_plugin(self.plugin_name)
                with plugin:
                    # noinspection PyProtectedMember
                    plugin._detection_thread.join()
            except Exception as e:
                self.logger.exception(e)
                self.logger.warning('Encountered an unexpected error, retrying in {} seconds'.format(self.retry_sleep))
                time.sleep(self.retry_sleep)


# vim:sw=4:ts=4:et:
