from typing import Optional, Sequence

from platypush.context import get_bus
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.assistant import AssistantPlugin

from ._assistant import Assistant


# pylint: disable=too-many-ancestors
class PicovoicePlugin(AssistantPlugin, RunnablePlugin):
    """
    A voice assistant that runs on your device, based on the `Picovoice
    <https://picovoice.ai/>`_ engine.

    .. note:: You will need a PicoVoice account and a personal access key to
        use this integration.

    You can get your personal access key by signing up at the `Picovoice
    console <https://console.picovoice.ai/>`_. You may be asked to submit a
    reason for using the service (feel free to mention a personal Platypush
    integration), and you will receive your personal access key.

    You may also be asked to select which products you want to use. The default
    configuration of this plugin requires the following:

        * **Porcupine**: wake-word engine, if you want the device to listen for
          a specific wake word in order to start the assistant.

        * **Cheetah**: speech-to-text engine, if you want your voice
          interactions to be transcribed into free text - either programmatically
          or when triggered by the wake word. Or:

        * **Rhino**: intent recognition engine, if you want to extract *intents*
          out of your voice commands - for instance, the phrase "set the living
          room temperature to 20 degrees" could be mapped to the intent with the
          following parameters: ``intent``: ``set_temperature``, ``room``:
          ``living_room``, ``temperature``: ``20``.

        * **Leopard**: speech-to-text engine aimed at offline transcription of
          audio files rather than real-time transcription.

    """

    def __init__(
        self,
        access_key: str,
        hotword_enabled: bool = True,
        stt_enabled: bool = True,
        intent_enabled: bool = False,
        keywords: Optional[Sequence[str]] = None,
        keyword_paths: Optional[Sequence[str]] = None,
        keyword_model_path: Optional[str] = None,
        **kwargs,
    ):
        """
        :param access_key: Your Picovoice access key. You can get it by signing
            up at the `Picovoice console <https://console.picovoice.ai/>`.
        :param hotword_enabled: Enable the wake-word engine (default: True).
            .. note:: The wake-word engine requires you to add Porcupine to the
                products available in your Picovoice account.
        :param stt_enabled: Enable the speech-to-text engine (default: True).
            .. note:: The speech-to-text engine requires you to add Cheetah to
                the products available in your Picovoice account.
        :param intent_enabled: Enable the intent recognition engine (default:
            False).
            .. note:: The intent recognition engine requires you to add Rhino
                to the products available in your Picovoice account.
        :param keywords: List of keywords to listen for (e.g. ``alexa``, ``ok
            google``...). Either ``keywords`` or ``keyword_paths`` must be
            provided if the wake-word engine is enabled. This list can include
            any of the default Picovoice keywords (available on the `Picovoice
            repository
            <https://github.com/Picovoice/porcupine/tree/master/resources/keyword_files>`_).
        :param keyword_paths: List of paths to the keyword files to listen for.
            Custom keyword files can be created using the `Picovoice console
            <https://console.picovoice.ai/ppn>`_ and downloaded from the
            console itself.
        :param keyword_model_path: If you are using a keyword file in a
            non-English language, you can provide the path to the model file
            for its language. Model files are available for all the supported
            languages through the `Picovoice repository
            <https://github.com/Picovoice/porcupine/tree/master/lib/common>`_.
        """
        super().__init__(**kwargs)
        self._assistant_args = {
            'stop_event': self._should_stop,
            'access_key': access_key,
            'hotword_enabled': hotword_enabled,
            'stt_enabled': stt_enabled,
            'intent_enabled': intent_enabled,
            'keywords': keywords,
            'keyword_paths': keyword_paths,
            'keyword_model_path': keyword_model_path,
        }

    @action
    def start_conversation(self, *_, **__):
        """
        Programmatically start a conversation with the assistant
        """

    @action
    def stop_conversation(self, *_, **__):
        """
        Programmatically stop a running conversation with the assistant
        """

    @action
    def mute(self, *_, **__):
        """
        Mute the microphone. Alias for :meth:`.set_mic_mute` with
        ``muted=True``.
        """

    @action
    def unmute(self, *_, **__):
        """
        Unmute the microphone. Alias for :meth:`.set_mic_mute` with
        ``muted=False``.
        """

    @action
    def set_mic_mute(self, muted: bool):
        """
        Programmatically mute/unmute the microphone.

        :param muted: Set to True or False.
        """

    @action
    def toggle_mute(self, *_, **__):
        """
        Toggle the mic mute state.
        """

    @action
    def send_text_query(self, *_, query: str, **__):
        """
        Send a text query to the assistant.

        This is equivalent to saying something to the assistant.

        :param query: Query to be sent.
        """

    def main(self):
        while not self.should_stop():
            self.logger.info('Starting Picovoice assistant')
            with Assistant(**self._assistant_args) as assistant:
                try:
                    for event in assistant:
                        if event:
                            get_bus().post(event)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error('Picovoice assistant error: %s', e, exc_info=True)
                    self.wait_stop(5)

    def stop(self):
        try:
            self.stop_conversation()
        except RuntimeError:
            pass

        super().stop()


# vim:sw=4:ts=4:et:
