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

class AssistantGoogleBackend(Backend):
    """ Class for the Google Assistant backend. It creates and event source
        that posts recognized phrases on the main bus """

    def __init__(self, credentials_file=os.path.join(
            os.path.expanduser('~/.config'),
            'google-oauthlib-tool', 'credentials.json'),
            on_conversation_start=None, on_conversation_end=None, **kwargs):
        """ Params:
            credentials_file -- Path to the Google OAuth credentials file
                (default: ~/.config/google-oauthlib-tool/credentials.json)
            on_conversation_start: Custom shell command to execute when a
                conversation starts (default: none)
            on_conversation_end: Custom shell command to execute when a
                conversation ends (default: none)
        """

        super().__init__(**kwargs)
        self.credentials_file = credentials_file
        self.on_conversation_start = on_conversation_start
        self.on_conversation_end = on_conversation_end

        with open(self.credentials_file, 'r') as f:
            self.credentials = google.oauth2.credentials.Credentials(token=None,
                                                                     **json.load(f))

        self.assistant = None

    def _process_event(self, event):
        logging.debug('Received assistant event: {}'.format(event))

        if event.type == EventType.ON_CONVERSATION_TURN_STARTED and self.on_conversation_start:
            subprocess.check_output(self.on_conversation_start,
                                    stderr=subprocess.STDOUT, shell=True)
        elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED and self.on_conversation_end:
            subprocess.check_output(self.on_conversation_end,
                                    stderr=subprocess.STDOUT, shell=True)
        elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
            phrase = event.args['text'].lower().strip()
            logging.info('Speech recognized: {}'.format(phrase))
            # self.on_message(event)

    def send_message(self, msg):
        # Cant' send a message on an event source, ignoring
        pass

    def on_stop(self):
        if self.producer:
            self.producer.flush()
            self.producer.close()

        if self.consumer:
            self.consumer.close()

    def run(self):
        super().run()

        with Assistant(self.credentials) as self.assistant:
            for event in self.assistant.start():
                self._process_event(event)


# vim:sw=4:ts=4:et:

