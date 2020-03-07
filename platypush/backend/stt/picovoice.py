from platypush.backend.stt import SttBackend


class SttPicovoiceBackend(SttBackend):
    """
    Backend for the PicoVoice speech-to-text engine plugin. Set this plugin to ``enabled`` if you
    want to run the speech-to-text engine continuously instead of programmatically using
    ``start_detection`` and ``stop_detection``.

    Requires:

        - The :class:`platypush.plugins.stt.deepspeech.SttPicovoicePlugin` plugin configured and its dependencies
          installed.

    """

    def __init__(self, *args, **kwargs):
        super().__init__('stt.picovoice', *args, **kwargs)


# vim:sw=4:ts=4:et:
