import logging
import json
import os
import time

from .. import Backend

from platypush.message import Message
from platypush.message.request import Request
from platypush.message.response import Response

class LocalBackend(Backend):
    """ Sends and receive messages on two distinct local FIFOs, one for
    the requests and one for the responses """

    def __init__(self, request_fifo, response_fifo, **kwargs):
        super().__init__(**kwargs)

        self.request_fifo  = request_fifo
        self.response_fifo = response_fifo

        try: os.mkfifo(self.request_fifo)
        except FileExistsError as e: pass

        try: os.mkfifo(self.response_fifo)
        except FileExistsError as e: pass


    def send_message(self, msg):
        fifo = self.response_fifo \
            if isinstance(msg, Response) or self._request_context \
            else self.request_fifo

        msg = '{}\n'.format(str(msg)).encode('utf-8')
        with open(fifo, 'wb') as f:
            f.write(msg)


    def _get_next_message(self):
        fifo = self.response_fifo if self._request_context else self.request_fifo
        with open(fifo, 'rb', 0) as f:
            msg = f.readline()

        return Message.build(msg) if len(msg) else None


    def on_stop(self):
        try: os.remove(self.request_fifo)
        except: pass

        try: os.remove(self.response_fifo)
        except: pass


    def run(self):
        super().run()
        logging.info('Initialized local backend on {} and {}'.
                     format(self.request_fifo, self.response_fifo))

        while not self.should_stop():
            try:
                msg = self._get_next_message()
                if not msg: continue
            except Exception as e:
                logging.exception(e)
                time.sleep(0.2)
                continue

            # logging.debug('Received message on the local backend: {}'.format(msg))
            logging.info('Received message on the local backend: {}'.format(msg))

            if self.should_stop(): break
            self.on_message(msg)


# vim:sw=4:ts=4:et:

