"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
.. license: MIT
"""

import json
import os
import time

from platypush.backend.assistant import AssistantBackend
from platypush.message.event.assistant import (
    ConversationStartEvent,
    ConversationEndEvent,
    ConversationTimeoutEvent,
    ResponseEvent,
    NoResponseEvent,
    SpeechRecognizedEvent,
    AlarmStartedEvent,
    AlarmEndEvent,
    TimerStartedEvent,
    TimerEndEvent,
    AlertStartedEvent,
    AlertEndEvent,
    MicMutedEvent,
    MicUnmutedEvent,
)


class AssistantGoogleBackend(AssistantBackend):
    """
    Google Assistant backend.

    It listens for voice commands and post conversation events on the bus.

    **WARNING**: The Google Assistant library used by this backend has officially been deprecated:
    https://developers.google.com/assistant/sdk/reference/library/python/. This backend still works on most of the
    devices where I use it, but its correct functioning is not guaranteed as the assistant library is no longer
    maintained.

    Triggers:

        * :class:`platypush.message.event.assistant.ConversationStartEvent` \
            when a new conversation starts
        * :class:`platypush.message.event.assistant.SpeechRecognizedEvent` \
            when a new voice command is recognized
        * :class:`platypush.message.event.assistant.NoResponse` \
            when a conversation returned no response
        * :class:`platypush.message.event.assistant.ResponseEvent` \
            when the assistant is speaking a response
        * :class:`platypush.message.event.assistant.ConversationTimeoutEvent` \
            when a conversation times out
        * :class:`platypush.message.event.assistant.ConversationEndEvent` \
            when a new conversation ends
        * :class:`platypush.message.event.assistant.AlarmStartedEvent` \
            when an alarm starts
        * :class:`platypush.message.event.assistant.AlarmEndEvent` \
            when an alarm ends
        * :class:`platypush.message.event.assistant.TimerStartedEvent` \
            when a timer starts
        * :class:`platypush.message.event.assistant.TimerEndEvent` \
            when a timer ends
        * :class:`platypush.message.event.assistant.MicMutedEvent` \
            when the microphone is muted.
        * :class:`platypush.message.event.assistant.MicUnmutedEvent` \
            when the microphone is un-muted.

    Requires:

        * **google-assistant-library** (``pip install google-assistant-library``)
        * **google-assistant-sdk[samples]** (``pip install google-assistant-sdk[samples]``)
        * **google-auth** (``pip install google-auth``)

    """

    _default_credentials_file = os.path.join(
        os.path.expanduser('~/.config'), 'google-oauthlib-tool', 'credentials.json'
    )

    def __init__(
        self,
        credentials_file=_default_credentials_file,
        device_model_id='Platypush',
        **kwargs
    ):
        """
        :param credentials_file: Path to the Google OAuth credentials file
            (default: ~/.config/google-oauthlib-tool/credentials.json).
            See
            https://developers.google.com/assistant/sdk/guides/library/python/embed/install-sample#generate_credentials
            for instructions to get your own credentials file.

        :type credentials_file: str

        :param device_model_id: Device model ID to use for the assistant
            (default: Platypush)
        :type device_model_id: str
        """

        super().__init__(**kwargs)
        self.credentials_file = credentials_file
        self.device_model_id = device_model_id
        self.credentials = None
        self.assistant = None
        self._has_error = False
        self._is_muted = False

        self.logger.info('Initialized Google Assistant backend')

    def _process_event(self, event):
        from google.assistant.library.event import EventType, AlertType

        self.logger.info('Received assistant event: {}'.format(event))
        self._has_error = False

        if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            self.bus.post(ConversationStartEvent(assistant=self))
        elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
            if not event.args.get('with_follow_on_turn'):
                self.bus.post(ConversationEndEvent(assistant=self))
        elif event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT:
            self.bus.post(ConversationTimeoutEvent(assistant=self))
        elif event.type == EventType.ON_NO_RESPONSE:
            self.bus.post(NoResponseEvent(assistant=self))
        elif (
            hasattr(EventType, 'ON_RENDER_RESPONSE')
            and event.type == EventType.ON_RENDER_RESPONSE
        ):
            self.bus.post(
                ResponseEvent(assistant=self, response_text=event.args.get('text'))
            )
            tts, args = self._get_tts_plugin()

            if tts and 'text' in event.args:
                self.stop_conversation()
                tts.say(text=event.args['text'], **args)
        elif (
            hasattr(EventType, 'ON_RESPONDING_STARTED')
            and event.type == EventType.ON_RESPONDING_STARTED
            and event.args.get('is_error_response', False) is True
        ):
            self.logger.warning('Assistant response error')
        elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
            phrase = event.args['text'].lower().strip()
            self.logger.info('Speech recognized: {}'.format(phrase))
            self.bus.post(SpeechRecognizedEvent(assistant=self, phrase=phrase))
        elif event.type == EventType.ON_ALERT_STARTED:
            if event.args.get('alert_type') == AlertType.ALARM:
                self.bus.post(AlarmStartedEvent(assistant=self))
            elif event.args.get('alert_type') == AlertType.TIMER:
                self.bus.post(TimerStartedEvent(assistant=self))
            else:
                self.bus.post(AlertStartedEvent(assistant=self))
        elif event.type == EventType.ON_ALERT_FINISHED:
            if event.args.get('alert_type') == AlertType.ALARM:
                self.bus.post(AlarmEndEvent(assistant=self))
            elif event.args.get('alert_type') == AlertType.TIMER:
                self.bus.post(TimerEndEvent(assistant=self))
            else:
                self.bus.post(AlertEndEvent(assistant=self))
        elif event.type == EventType.ON_ASSISTANT_ERROR:
            self._has_error = True
            if event.args.get('is_fatal'):
                self.logger.error('Fatal assistant error')
            else:
                self.logger.warning('Assistant error')
        if event.type == EventType.ON_MUTED_CHANGED:
            self._is_muted = event.args.get('is_muted')
            event = MicMutedEvent() if self._is_muted else MicUnmutedEvent()
            self.bus.post(event)

    def start_conversation(self):
        """Starts an assistant conversation"""
        if self.assistant:
            self.assistant.start_conversation()

    def stop_conversation(self):
        """Stops an assistant conversation"""
        if self.assistant:
            self.assistant.stop_conversation()

    def set_mic_mute(self, muted):
        if not self.assistant:
            self.logger.warning('Assistant not running')
            return

        self.assistant.set_mic_mute(muted)

    def is_muted(self) -> bool:
        return self._is_muted

    def send_text_query(self, query):
        if not self.assistant:
            self.logger.warning('Assistant not running')
            return

        self.assistant.send_text_query(query)

    def run(self):
        import google.oauth2.credentials
        from google.assistant.library import Assistant

        super().run()

        with open(self.credentials_file, 'r') as f:
            self.credentials = google.oauth2.credentials.Credentials(
                token=None, **json.load(f)
            )

        while not self.should_stop():
            self._has_error = False

            with Assistant(self.credentials, self.device_model_id) as assistant:
                self.assistant = assistant
                for event in assistant.start():
                    if not self.is_detecting():
                        self.logger.info(
                            'Assistant event received but detection is currently paused'
                        )
                        continue

                    self._process_event(event)
                    if self._has_error:
                        self.logger.info(
                            'Restarting the assistant after an unrecoverable error'
                        )
                        time.sleep(5)
                        break


# vim:sw=4:ts=4:et:
