from platypush.backend.stt import SttBackend


class SttPicovoiceHotwordBackend(SttBackend):
    """
    Backend for the PicoVoice hotword detection plugin. Set this plugin to ``enabled`` if you
    want to run the hotword engine continuously instead of programmatically using
    ``start_detection`` and ``stop_detection``.

    Requires:

        - The :class:`platypush.plugins.stt.deepspeech.SttPicovoiceHotwordPlugin` plugin configured and its dependencies
          installed.

    """

    def __init__(self, *args, **kwargs):
        super().__init__('stt.picovoice.hotword', *args, **kwargs)


# vim:sw=4:ts=4:et:
