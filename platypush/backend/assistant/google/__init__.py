import logging
import json
import os
import subprocess
import time

import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file

from platypush.backend import Backend
from platypush.message.event.assistant import \
    ConversationStartEvent, ConversationEndEvent, SpeechRecognizedEvent

class AssistantGoogleBackend(Backend):
    """ Class for the Google Assistant backend. It creates and event source
        that posts recognized phrases on the main bus """

    def __init__(self, credentials_file=os.path.join(
            os.path.expanduser('~/.config'),
            'google-oauthlib-tool', 'credentials.json'),
            device_model_id='Platypush', **kwargs):
        """ Params:
            credentials_file -- Path to the Google OAuth credentials file
                (default: ~/.config/google-oauthlib-tool/credentials.json)
            device_model_id  -- Device model ID to use for the assistant
                (default: Platypush)
        """

        super().__init__(**kwargs)
        self.credentials_file = credentials_file
        self.device_model_id = device_model_id
        self.assistant = None

        with open(self.credentials_file, 'r') as f:
            self.credentials = google.oauth2.credentials.Credentials(token=None,
                                                                     **json.load(f))
        logging.info('Initialized Google Assistant backend')

    def _process_event(self, event):
        logging.info('Received assistant event: {}'.format(event))

        if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            self.bus.post(ConversationStartEvent())
        elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
            self.bus.post(ConversationEndEvent())
        elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
            phrase = event.args['text'].lower().strip()
            logging.info('Speech recognized: {}'.format(phrase))
            self.bus.post(SpeechRecognizedEvent(phrase=phrase))


    def start_conversation(self):
        if self.assistant: self.assistant.start_conversation()


    def stop_conversation(self):
        if self.assistant: self.assistant.stop_conversation()


    def send_message(self, msg):
        # Can't send a message on an event source, ignoring
        # TODO Make a class for event sources like these. Event sources
        # would be a subset of the backends which can fire events on the bus
        # but not receive requests or process responses.
        pass

    def run(self):
        super().run()

        with Assistant(self.credentials, self.device_model_id) as assistant:
            self.assistant = assistant
            for event in assistant.start():
                self._process_event(event)


# vim:sw=4:ts=4:et:

