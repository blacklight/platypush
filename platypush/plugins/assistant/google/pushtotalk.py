"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import json
import logging
import os

import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials

import googlesamples.assistant.grpc.audio_helpers as audio_helpers
import googlesamples.assistant.grpc.device_helpers as device_helpers

from platypush.context import get_bus
from platypush.message.event.assistant import ConversationStartEvent, \
    ConversationEndEvent, SpeechRecognizedEvent, VolumeChangedEvent, \
    ResponseEvent

from platypush.plugins import action
from platypush.plugins.assistant import AssistantPlugin
from platypush.plugins.assistant.google.lib import SampleAssistant

class AssistantGooglePushtotalkPlugin(AssistantPlugin):
    """
    Plugin for the Google Assistant push-to-talk API.

    Triggers:

        * :class:`platypush.message.event.assistant.ConversationStartEvent` \
            when a new conversation starts
        * :class:`platypush.message.event.assistant.SpeechRecognizedEvent` \
            when a new voice command is recognized
        * :class:`platypush.message.event.assistant.ConversationEndEvent` \
            when a new conversation ends

    Requires:

        * **tenacity** (``pip install tenacity``)
        * **google-assistant-sdk** (``pip install google-assistant-sdk[samples]``)
    """

    api_endpoint = 'embeddedassistant.googleapis.com'
    audio_sample_rate = audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE
    audio_sample_width = audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH
    audio_iter_size = audio_helpers.DEFAULT_AUDIO_ITER_SIZE
    audio_block_size = audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE
    audio_flush_size = audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
    grpc_deadline = 60 * 3 + 5

    def __init__(self,
                 credentials_file=os.path.join(
                     os.path.expanduser('~'), '.config',
                     'google-oauthlib-tool', 'credentials.json'),
                 device_config=os.path.join(
                     os.path.expanduser('~'), '.config', 'googlesamples-assistant',
                     'device_config.json'),
                 language='en-US', **kwargs):
        """
        :param credentials_file: Path to the Google OAuth credentials file \
            (default: ~/.config/google-oauthlib-tool/credentials.json). \
            See https://developers.google.com/assistant/sdk/guides/library/python/embed/install-sample#generate_credentials \
            for instructions to get your own credentials file.
        :type credentials_file: str

        :param device_config: Path to device_config.json. Register your device \
            (see https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device) \
            and create a project, then run the pushtotalk.py script from \
            googlesamples to create your device_config.json
        :type device_config: str

        :param language: Assistant language (default: en-US)
        :type language: str
        """

        super().__init__(**kwargs)

        self.language = language
        self.credentials_file = credentials_file
        self.device_config = device_config
        self.assistant = None
        self.interactions = []

        with open(self.device_config) as f:
            device = json.load(f)
            self.device_id = device['id']
            self.device_model_id = device['model_id']

        # Load OAuth 2.0 credentials.
        try:
            with open(self.credentials_file, 'r') as f:
                self.credentials = google.oauth2.credentials.Credentials(token=None,
                                                                    **json.load(f))
                self.http_request = google.auth.transport.requests.Request()
                self.credentials.refresh(self.http_request)
        except Exception as ex:
            self.logger.error('Error loading credentials: %s', str(ex))
            self.logger.error('Run google-oauthlib-tool to initialize '
                              'new OAuth 2.0 credentials.')
            raise

        self.grpc_channel = None
        self.conversation_stream = None
        self.device_handler = None

    def _init_assistant(self):
        self.interactions = []

        # Create an authorized gRPC channel.
        self.grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
            self.credentials, self.http_request, self.api_endpoint)

        self.logger.info('Connecting to {}'.format(self.api_endpoint))

        # Configure audio source and sink.
        audio_device = None
        audio_source = audio_device = (
            audio_device or audio_helpers.SoundDeviceStream(
                sample_rate=self.audio_sample_rate,
                sample_width=self.audio_sample_width,
                block_size=self.audio_block_size,
                flush_size=self.audio_flush_size
            )
        )

        audio_sink = audio_device = (
            audio_device or audio_helpers.SoundDeviceStream(
                sample_rate=self.audio_sample_rate,
                sample_width=self.audio_sample_width,
                block_size=self.audio_block_size,
                flush_size=self.audio_flush_size
            )
        )

        # Create conversation stream with the given audio source and sink.
        self.conversation_stream = audio_helpers.ConversationStream(
            source=audio_source,
            sink=audio_sink,
            iter_size=self.audio_iter_size,
            sample_width=self.audio_sample_width,
        )

        self.device_handler = device_helpers.DeviceRequestHandler(self.device_id)

    def on_conversation_start(self):
        """ Conversation start handler """
        def handler():
            get_bus().post(ConversationStartEvent())

        return handler

    def on_conversation_end(self):
        """ Conversation end handler """
        def handler(with_follow_on_turn):
            get_bus().post(ConversationEndEvent(with_follow_on_turn=with_follow_on_turn))

        return handler

    def on_speech_recognized(self):
        """ Speech recognized handler """
        def handler(phrase):
            get_bus().post(SpeechRecognizedEvent(phrase=phrase))
            self.interactions.append({'request': phrase})

        return handler

    def on_volume_changed(self):
        """ Volume changed event """
        def handler(volume):
            get_bus().post(VolumeChangedEvent(volume=volume))

        return handler

    def on_response(self):
        """ Response handler """
        def handler(response):
            get_bus().post(ResponseEvent(response_text=response))

            if not self.interactions:
                self.interactions.append({'response': response})
            else:
                self.interactions[-1]['response'] = response

        return handler

    def on_device_action(self):
        """ Device action handler """
        def handler(request):
            self.logger.info('Received request: {}'.format(request))

        return handler

    @action
    def start_conversation(self, language=None):
        """
        Start a conversation

        :param language: Language code override (default: default configured
            language)
        :type language: str

        :returns: A list of the interactions that happen within the conversation::

                [
                    {
                        "request": "request 1",
                        "response": "response 1"
                    },
                    {
                        "request": "request 2",
                        "response": "response 2"
                    },
                ]
        """

        if not language:
            language = self.language

        self._init_assistant()

        with SampleAssistant(language_code=language,
                             device_model_id=self.device_model_id,
                             device_id=self.device_id,
                             conversation_stream=self.conversation_stream,
                             display=None,
                             channel=self.grpc_channel,
                             deadline_sec=self.grpc_deadline,
                             device_handler=self.on_device_action(),
                             on_conversation_start=self.on_conversation_start(),
                             on_conversation_end=self.on_conversation_end(),
                             on_volume_changed=self.on_volume_changed(),
                             on_response=self.on_response(),
                             on_speech_recognized=self.on_speech_recognized()) as self.assistant:
            continue_conversation = True

            while continue_conversation:
                try:
                    continue_conversation = self.assistant.assist()
                except Exception as e:
                    self.logger.warning('Unhandled assistant exception: {}'.format(str(e)))
                    self.logger.exception(e)
                    self._init_assistant()

        return self.interactions

    @action
    def stop_conversation(self):
        """ Stop a conversation """
        if self.assistant:
            self.assistant.play_response = False

            if self.conversation_stream:
                self.conversation_stream.stop_playback()
                self.conversation_stream.stop_recording()

            get_bus().post(ConversationEndEvent())


# vim:sw=4:ts=4:et:
