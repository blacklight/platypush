import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.plugins.stt.deepspeech import SttDeepspeechPlugin


class SttDeepspeechBackend(Backend):
    """
    Backend for the Mozilla Deepspeech speech-to-text engine plugin. Set this plugin to ``enabled`` if you
    want to run the speech-to-text engine continuously instead of programmatically using
    ``start_detection`` and ``stop_detection``.

    Requires:

        - The :class:`platypush.plugins.stt.deepspeech.SttDeepspeechPlugin` plugin configured and its dependencies
          installed, as well as the language model files.

    """

    def __init__(self, retry_sleep: float = 5.0, *args, **kwargs):
        """
        :param retry_sleep: Number of seconds the backend will wait on failure before re-initializing the plugin
            (default: 5 seconds).
        """
        super().__init__(*args, **kwargs)
        self.retry_sleep = retry_sleep

    def run(self):
        super().run()
        self.logger.info('Starting Mozilla Deepspeech speech-to-text backend')

        while not self.should_stop():
            try:
                plugin: SttDeepspeechPlugin = get_plugin('stt.deepspeech')
                with plugin:
                    # noinspection PyProtectedMember
                    plugin._detection_thread.join()
            except Exception as e:
                self.logger.exception(e)
                self.logger.warning('Deepspeech backend encountered an unexpected error, retrying in {} seconds'.
                                    format(self.retry_sleep))

                time.sleep(self.retry_sleep)


# vim:sw=4:ts=4:et:
