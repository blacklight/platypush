from platypush.backend.stt import SttBackend


class SttPicovoiceSpeechBackend(SttBackend):
    """
    Backend for the PicoVoice speech detection plugin. Set this plugin to ``enabled`` if you
    want to run the speech engine continuously instead of programmatically using
    ``start_detection`` and ``stop_detection``.

    Requires:

        - The :class:`platypush.plugins.stt.deepspeech.SttPicovoiceSpeechPlugin` plugin configured and its dependencies
          installed.

    """

    def __init__(self, *args, **kwargs):
        super().__init__('stt.picovoice.speech', *args, **kwargs)


# vim:sw=4:ts=4:et:
