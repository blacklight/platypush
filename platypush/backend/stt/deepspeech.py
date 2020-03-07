from platypush.backend.stt import SttBackend


class SttDeepspeechBackend(SttBackend):
    """
    Backend for the Mozilla Deepspeech speech-to-text engine plugin. Set this plugin to ``enabled`` if you
    want to run the speech-to-text engine continuously instead of programmatically using
    ``start_detection`` and ``stop_detection``.

    Requires:

        - The :class:`platypush.plugins.stt.deepspeech.SttDeepspeechPlugin` plugin configured and its dependencies
          installed, as well as the language model files.

    """

    def __init__(self, *args, **kwargs):
        super().__init__('stt.deepspeech', *args, **kwargs)


# vim:sw=4:ts=4:et:
