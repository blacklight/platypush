import logging
import json
import os
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
            'google-oauthlib-tool', 'credentials.json') , **kwargs):
        """ Params:
            credentials_file -- Path to the Google OAuth credentials file
                (default: ~/.config/google-oauthlib-tool/credentials.json) """

        super().__init__(**kwargs)
        self.credentials_file = credentials_file

        with open(args.credentials, 'r') as f:
            self.credentials = google.oauth2.credentials.Credentials(token=None,
                                                                     **json.load(f))

        self.assistant = None

    def _process_event(self, event):
        logging.info('Received assistant event: {}'.format(event))
        # self.on_message(event)

    def send_message(self, msg):
        raise NotImplementedError("Cannot send messages on an event source")

    def on_stop(self):
        if self.producer:
            self.producer.flush()
            self.producer.close()

        if self.consumer:
            self.consumer.close()

    def run(self):
        super().run()

        with Assistant(self.credentials) as self.assistant:
            for event in assistant.start():
                self._process_event(event)


# vim:sw=4:ts=4:et:

