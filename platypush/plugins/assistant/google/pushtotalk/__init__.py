import json
import os
from typing import Optional, Dict, Any

from platypush.context import get_bus, get_plugin
from platypush.message.event.assistant import (
    ConversationStartEvent,
    ConversationEndEvent,
    SpeechRecognizedEvent,
    VolumeChangedEvent,
    ResponseEvent,
)

from platypush.message.event.google import GoogleDeviceOnOffEvent

from platypush.plugins import action
from platypush.plugins.assistant import AssistantPlugin


class AssistantGooglePushtotalkPlugin(AssistantPlugin):
    """
    Plugin for the Google Assistant push-to-talk API.

    Triggers:

        * :class:`platypush.message.event.assistant.ConversationStartEvent`
            when a new conversation starts
        * :class:`platypush.message.event.assistant.SpeechRecognizedEvent`
            when a new voice command is recognized
        * :class:`platypush.message.event.assistant.ConversationEndEvent`
            when a new conversation ends

    Requires:

        * **tenacity** (``pip install tenacity``)
        * **google-assistant-sdk** (``pip install google-assistant-sdk[samples]``)
        * **google-auth** (``pip install google-auth``)

    """

    api_endpoint = 'embeddedassistant.googleapis.com'
    grpc_deadline = 60 * 3 + 5
    device_handler = None
    _default_credentials_file = os.path.join(
        os.path.expanduser('~'),
        '.config',
        'google-oauthlib-tool',
        'credentials.json',
    )

    _default_device_config = os.path.join(
        os.path.expanduser('~'),
        '.config',
        'googlesamples-assistant',
        'device_config.json',
    )

    def __init__(
        self,
        credentials_file=_default_credentials_file,
        device_config=_default_device_config,
        language='en-US',
        play_response=True,
        tts_plugin=None,
        tts_args=None,
        **kwargs
    ):
        """
        :param credentials_file: Path to the Google OAuth credentials file
            (default: ~/.config/google-oauthlib-tool/credentials.json).
            See
            https://developers.google.com/assistant/sdk/guides/library/python/embed/install-sample#generate_credentials
            for instructions to get your own credentials file.
        :type credentials_file: str

        :param device_config: Path to device_config.json. Register your device
            (see https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device)
            and create a project, then run the pushtotalk.py script from
            googlesamples to create your device_config.json
        :type device_config: str

        :param language: Assistant language (default: en-US)
        :type language: str

        :param play_response: If True (default) then the plugin will play the assistant response upon processed
            response. Otherwise nothing will be played - but you may want to handle the ``ResponseEvent`` manually.
        :type play_response: bool

        :param tts_plugin: Optional text-to-speech plugin to be used to process response text.
        :type tts_plugin: str

        :param tts_args: Optional arguments for the TTS plugin ``say`` method.
        :type tts_args: dict
        """

        import googlesamples.assistant.grpc.audio_helpers as audio_helpers

        super().__init__(**kwargs)

        self.audio_sample_rate = audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE
        self.audio_sample_width = audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH
        self.audio_iter_size = audio_helpers.DEFAULT_AUDIO_ITER_SIZE
        self.audio_block_size = audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE
        self.audio_flush_size = audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE

        self.language = language
        self.credentials_file = credentials_file
        self.device_config = device_config
        self.play_response = play_response
        self.tts_plugin = tts_plugin
        self.tts_args = tts_args or {}
        self.assistant = None
        self.interactions = []

        with open(self.device_config) as f:
            device = json.load(f)
            self.device_id = device['id']
            self.device_model_id = device['model_id']

        # Load OAuth 2.0 credentials.
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request

            with open(self.credentials_file, 'r') as f:
                self.credentials = Credentials(token=None, **json.load(f))
                self.http_request = Request()
                self.credentials.refresh(self.http_request)
        except Exception as ex:
            self.logger.error('Error loading credentials: %s', str(ex))
            self.logger.error(
                'Run google-oauthlib-tool to initialize ' 'new OAuth 2.0 credentials.'
            )
            raise

        self.grpc_channel = None
        self.conversation_stream = None

    def _init_assistant(self):
        import googlesamples.assistant.grpc.audio_helpers as audio_helpers
        from google.auth.transport.grpc import secure_authorized_channel

        self.interactions = []

        # Create an authorized gRPC channel.
        self.grpc_channel = secure_authorized_channel(
            self.credentials, self.http_request, self.api_endpoint
        )
        self.logger.info('Connecting to {}'.format(self.api_endpoint))

        # Configure audio source and sink.
        audio_device = None
        audio_source = audio_device = audio_device or audio_helpers.SoundDeviceStream(
            sample_rate=self.audio_sample_rate,
            sample_width=self.audio_sample_width,
            block_size=self.audio_block_size,
            flush_size=self.audio_flush_size,
        )

        audio_sink = audio_device or audio_helpers.SoundDeviceStream(
            sample_rate=self.audio_sample_rate,
            sample_width=self.audio_sample_width,
            block_size=self.audio_block_size,
            flush_size=self.audio_flush_size,
        )

        # Create conversation stream with the given audio source and sink.
        self.conversation_stream = audio_helpers.ConversationStream(
            source=audio_source,
            sink=audio_sink,
            iter_size=self.audio_iter_size,
            sample_width=self.audio_sample_width,
        )

        self._install_device_handlers()

    def on_conversation_start(self):
        """Conversation start handler"""

        def handler():
            get_bus().post(ConversationStartEvent(assistant=self))

        return handler

    def on_conversation_end(self):
        """Conversation end handler"""

        def handler(with_follow_on_turn):
            get_bus().post(
                ConversationEndEvent(
                    assistant=self, with_follow_on_turn=with_follow_on_turn
                )
            )

        return handler

    def on_speech_recognized(self):
        """Speech recognized handler"""

        def handler(phrase):
            get_bus().post(SpeechRecognizedEvent(assistant=self, phrase=phrase))
            self.interactions.append({'request': phrase})

        return handler

    def on_volume_changed(self):
        """Volume changed event"""

        def handler(volume):
            get_bus().post(VolumeChangedEvent(assistant=self, volume=volume))

        return handler

    def on_response(self):
        """Response handler"""

        def handler(response):
            get_bus().post(ResponseEvent(assistant=self, response_text=response))

            if not self.interactions:
                self.interactions.append({'response': response})
            else:
                self.interactions[-1]['response'] = response

            if self.tts_plugin:
                tts = get_plugin(self.tts_plugin)
                tts.say(response, **self.tts_args)

        return handler

    @action
    def start_conversation(
        self,
        *_,
        language: Optional[str] = None,
        tts_plugin: Optional[str] = None,
        tts_args: Optional[Dict[str, Any]] = None,
        **__
    ):
        """
        Start a conversation

        :param language: Language code override (default: default configured language).
        :param tts_plugin: Optional text-to-speech plugin to be used for rendering text.
        :param tts_args: Optional arguments for the TTS plugin say method.
        :returns: A list of the interactions that happen within the conversation.

          .. code-block:: json

             [
                 {
                     "request": "request 1",
                     "response": "response 1"
                 },
                 {
                     "request": "request 2",
                     "response": "response 2"
                 }
             ]

        """

        from platypush.plugins.assistant.google.lib import SampleAssistant

        self.tts_plugin = tts_plugin
        self.tts_args = tts_args
        language = language or self.language
        play_response = False if self.tts_plugin else self.play_response

        self._init_assistant()
        self.on_conversation_start()

        with SampleAssistant(
            language_code=language,
            device_model_id=self.device_model_id,
            device_id=self.device_id,
            conversation_stream=self.conversation_stream,
            display=None,
            channel=self.grpc_channel,
            deadline_sec=self.grpc_deadline,
            play_response=play_response,
            device_handler=self.device_handler,
            on_conversation_start=self.on_conversation_start(),
            on_conversation_end=self.on_conversation_end(),
            on_volume_changed=self.on_volume_changed(),
            on_response=self.on_response(),
            on_speech_recognized=self.on_speech_recognized(),
        ) as self.assistant:
            continue_conversation = True

            while continue_conversation:
                try:
                    continue_conversation = self.assistant.assist()
                except Exception as e:
                    self.logger.warning(
                        'Unhandled assistant exception: {}'.format(str(e))
                    )
                    self.logger.exception(e)
                    self._init_assistant()

        return self.interactions

    @action
    def stop_conversation(self):
        if self.assistant:
            self.assistant.play_response = False

            if self.conversation_stream:
                self.conversation_stream.stop_playback()
                self.conversation_stream.stop_recording()

            get_bus().post(ConversationEndEvent(assistant=self))

    @action
    def set_mic_mute(self, muted: bool = True):
        """
        Programmatically mute/unmute the microphone.

        :param muted: Set to True or False.
        """
        if not self.conversation_stream:
            self.logger.warning('The assistant is not running')
            return

        if muted:
            self.conversation_stream.stop_recording()
        else:
            self.conversation_stream.start_recording()

    def _install_device_handlers(self):
        import googlesamples.assistant.grpc.device_helpers as device_helpers

        self.device_handler = device_helpers.DeviceRequestHandler(self.device_id)

        @self.device_handler.command('action.devices.commands.OnOff')
        def handler(on):  # type: ignore
            get_bus().post(
                GoogleDeviceOnOffEvent(
                    device_id=self.device_id,
                    device_model_id=self.device_model_id,
                    on=on,
                )
            )


# vim:sw=4:ts=4:et:
