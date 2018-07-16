import json
import logging
import os
import threading
import time

import grpc
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials
import googlesamples.assistant.grpc.audio_helpers as audio_helpers
import googlesamples.assistant.grpc.device_helpers as device_helpers
import googlesamples.assistant.grpc.assistant_helpers as assistant_helpers

from tenacity import retry, stop_after_attempt, retry_if_exception
from google.assistant.embedded.v1alpha2 import (
    embedded_assistant_pb2,
    embedded_assistant_pb2_grpc
)


from platypush.backend import Backend
from platypush.message.event.assistant import \
    ConversationStartEvent, ConversationEndEvent, SpeechRecognizedEvent


class AssistantGooglePushtotalkBackend(Backend):
    """
    Google Assistant pushtotalk backend. Instead of listening for the "OK
    Google" hotword like the assistant.google backend, this implementation
    programmatically starts a conversation upon start_conversation() method
    call. Use this backend on devices that don't have an Assistant SDK package
    (e.g. arm6 devices like the RaspberryPi Zero or the RaspberryPi 1).

    Triggers:

        * :class:`platypush.message.event.assistant.ConversationStartEvent` when a new conversation starts
        * :class:`platypush.message.event.assistant.SpeechRecognizedEvent` when a new voice command is recognized
        * :class:`platypush.message.event.assistant.ConversationEndEvent` when a new conversation ends

    Requires:

        * **tenacity** (``pip install tenacity``)
        * **grpc** (``pip install grpc``)
        * **google-assistant-grpc** (``pip install google-assistant-grpc``)
    """

    api_endpoint = 'embeddedassistant.googleapis.com'
    audio_sample_rate = audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE
    audio_sample_width = audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH
    audio_iter_size = audio_helpers.DEFAULT_AUDIO_ITER_SIZE
    audio_block_size = audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE
    audio_flush_size = audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
    grpc_deadline = 60 * 3 + 5

    def __init__(self, credentials_file=os.path.join(
                os.path.expanduser('~'), '.config',
                'google-oauthlib-tool', 'credentials.json'),
            device_config=os.path.join(
                os.path.expanduser('~'), '.config', 'googlesamples-assistant',
                'device_config.json'),
            lang='en-US',
            conversation_start_fifo = os.path.join(os.path.sep, 'tmp', 'pushtotalk.fifo'),
            *args, **kwargs):
        """
        :param credentials_file: Path to the Google OAuth credentials file (default: ~/.config/google-oauthlib-tool/credentials.json). See https://developers.google.com/assistant/sdk/guides/library/python/embed/install-sample#generate_credentials for how to get your own credentials file.
        :type credentials_file: str

        :param device_config: Path to device_config.json. Register your device (see https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device) and create a project, then run the pushtotalk.py script from googlesamples to create your device_config.json
        :type device_config: str

        :param lang: Assistant language (default: en-US)
        :type lang: str
        """

        super().__init__(*args, **kwargs)

        self.lang = lang
        self.credentials_file = credentials_file
        self.device_config = device_config
        self.conversation_start_fifo = conversation_start_fifo
        self.assistant = None

        try:
            os.mkfifo(self.conversation_start_fifo)
        except FileExistsError:
            pass

        with open(self.device_config) as f:
            device = json.load(f)
            self.device_id = device['id']
            self.device_model_id = device['model_id']

        # Load OAuth 2.0 credentials.
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = google.oauth2.credentials.Credentials(token=None,
                                                                    **json.load(f))
                http_request = google.auth.transport.requests.Request()
                credentials.refresh(http_request)
        except:
            self.logger.error('Error loading credentials: %s', e)
            self.logger.error('Run google-oauthlib-tool to initialize '
                        'new OAuth 2.0 credentials.')
            raise

        # Create an authorized gRPC channel.
        self.grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
            credentials, http_request, self.api_endpoint)
        self.logger.info('Connecting to %s', self.api_endpoint)

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

    def start_conversation(self):
        """ Start a conversation """
        if self.assistant:
            with open(self.conversation_start_fifo, 'w') as f:
                f.write('1')

    def stop_conversation(self):
        """ Stop a conversation """
        if self.assistant:
            self.conversation_stream.stop_playback()
            self.bus.post(ConversationEndEvent())

    def send_message(self, msg):
        pass

    def on_conversation_start(self):
        self.bus.post(ConversationStartEvent())

    def on_conversation_end(self):
        self.bus.post(ConversationEndEvent())

    def on_speech_recognized(self, speech):
        self.bus.post(SpeechRecognizedEvent(phrase=speech))

    def run(self):
        super().run()

        with SampleAssistant(self.lang, self.device_model_id, self.device_id,
                            self.conversation_stream,
                            self.grpc_channel, self.grpc_deadline,
                            self.device_handler,
                            on_conversation_start=self.on_conversation_start,
                            on_conversation_end=self.on_conversation_end,
                            on_speech_recognized=self.on_speech_recognized) as self.assistant:
            while not self.should_stop():
                with open(self.conversation_start_fifo, 'r') as f:
                    for line in f: pass

                self.logger.info('Received conversation start event')
                continue_conversation = True
                user_request = None

                while continue_conversation:
                    (user_request, continue_conversation) = self.assistant.assist()

                self.on_conversation_end()


class SampleAssistant(object):
    """Sample Assistant that supports conversations and device actions.

    Args:
      device_model_id: identifier of the device model.
      device_id: identifier of the registered device instance.
      conversation_stream(ConversationStream): audio stream for recording query and playing back assistant answer.
      channel: authorized gRPC channel for connection to the Google Assistant API.
      deadline_sec: gRPC deadline in seconds for Google Assistant API call.
      device_handler: callback for device actions.
    """

    END_OF_UTTERANCE = embedded_assistant_pb2.AssistResponse.END_OF_UTTERANCE
    DIALOG_FOLLOW_ON = embedded_assistant_pb2.DialogStateOut.DIALOG_FOLLOW_ON
    CLOSE_MICROPHONE = embedded_assistant_pb2.DialogStateOut.CLOSE_MICROPHONE

    def __init__(self, language_code, device_model_id, device_id,
                 conversation_stream,
                 channel, deadline_sec, device_handler,
                 on_conversation_start=None,
                 on_conversation_end=None,
                 on_speech_recognized=None):
        self.language_code = language_code
        self.device_model_id = device_model_id
        self.device_id = device_id
        self.conversation_stream = conversation_stream
        self.logger = logging.getLogger(__name__)

        self.on_conversation_start = on_conversation_start
        self.on_conversation_end = on_conversation_end
        self.on_speech_recognized = on_speech_recognized

        # Opaque blob provided in AssistResponse that,
        # when provided in a follow-up AssistRequest,
        # gives the Assistant a context marker within the current state
        # of the multi-Assist()-RPC "conversation".
        # This value, along with MicrophoneMode, supports a more natural
        # "conversation" with the Assistant.
        self.conversation_state = None

        # Create Google Assistant API gRPC client.
        self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(
            channel
        )
        self.deadline = deadline_sec

        self.device_handler = device_handler

    def __enter__(self):
        return self

    def __exit__(self, etype, e, traceback):
        if e:
            return False
        self.conversation_stream.close()

    def is_grpc_error_unavailable(e):
        is_grpc_error = isinstance(e, grpc.RpcError)
        if is_grpc_error and (e.code() == grpc.StatusCode.UNAVAILABLE):
            self.logger.error('grpc unavailable error: %s', e)
            return True
        return False

    @retry(reraise=True, stop=stop_after_attempt(3),
           retry=retry_if_exception(is_grpc_error_unavailable))
    def assist(self):
        """Send a voice request to the Assistant and playback the response.

        Returns: True if conversation should continue.
        """
        continue_conversation = False
        device_actions_futures = []

        self.conversation_stream.start_recording()
        self.logger.info('Recording audio request.')

        if self.on_conversation_start:
            self.on_conversation_start()

        def iter_assist_requests():
            for c in self.gen_assist_requests():
                assistant_helpers.log_assist_request_without_audio(c)
                yield c
            self.conversation_stream.start_playback()

        user_request = None

        # This generator yields AssistResponse proto messages
        # received from the gRPC Google Assistant API.
        for resp in self.assistant.Assist(iter_assist_requests(),
                                          self.deadline):
            assistant_helpers.log_assist_response_without_audio(resp)
            if resp.event_type == self.END_OF_UTTERANCE:
                self.logger.info('End of audio request detected')
                self.conversation_stream.stop_recording()
            if resp.speech_results:
                user_request = ' '.join(
                    r.transcript for r in resp.speech_results)

                self.logger.info('Transcript of user request: "%s".', user_request)
                self.logger.info('Playing assistant response.')
            if len(resp.audio_out.audio_data) > 0:
                self.conversation_stream.write(resp.audio_out.audio_data)
            if resp.dialog_state_out.conversation_state:
                conversation_state = resp.dialog_state_out.conversation_state
                self.logger.debug('Updating conversation state.')
                self.conversation_state = conversation_state
            if resp.dialog_state_out.volume_percentage != 0:
                volume_percentage = resp.dialog_state_out.volume_percentage
                self.logger.info('Setting volume to %s%%', volume_percentage)
                self.conversation_stream.volume_percentage = volume_percentage
            if resp.dialog_state_out.microphone_mode == self.DIALOG_FOLLOW_ON:
                continue_conversation = True
                self.logger.info('Expecting follow-on query from user.')
            elif resp.dialog_state_out.microphone_mode == self.CLOSE_MICROPHONE:
                continue_conversation = False
            if resp.device_action.device_request_json:
                device_request = json.loads(
                    resp.device_action.device_request_json
                )
                fs = self.device_handler(device_request)
                if fs:
                    device_actions_futures.extend(fs)

        if len(device_actions_futures):
            self.logger.info('Waiting for device executions to complete.')
            concurrent.futures.wait(device_actions_futures)

        self.logger.info('Finished playing assistant response.')

        try:
            self.conversation_stream.stop_playback()
        except:
            pass

        if user_request and self.on_speech_recognized:
            self.on_speech_recognized(user_request)

        return (user_request, continue_conversation)

    def gen_assist_requests(self):
        """Yields: AssistRequest messages to send to the API."""

        dialog_state_in = embedded_assistant_pb2.DialogStateIn(
                language_code=self.language_code,
                conversation_state=b''
            )
        if self.conversation_state:
            self.logger.debug('Sending conversation state.')
            dialog_state_in.conversation_state = self.conversation_state
        config = embedded_assistant_pb2.AssistConfig(
            audio_in_config=embedded_assistant_pb2.AudioInConfig(
                encoding='LINEAR16',
                sample_rate_hertz=self.conversation_stream.sample_rate,
            ),
            audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                encoding='LINEAR16',
                sample_rate_hertz=self.conversation_stream.sample_rate,
                volume_percentage=self.conversation_stream.volume_percentage,
            ),
            dialog_state_in=dialog_state_in,
            device_config=embedded_assistant_pb2.DeviceConfig(
                device_id=self.device_id,
                device_model_id=self.device_model_id,
            )
        )
        # The first AssistRequest must contain the AssistConfig
        # and no audio data.
        yield embedded_assistant_pb2.AssistRequest(config=config)
        for data in self.conversation_stream:
            # Subsequent requests need audio data, but not config.
            yield embedded_assistant_pb2.AssistRequest(audio_in=data)


# vim:sw=4:ts=4:et:

