import logging
import json
import os
import time

from .. import Backend

class LocalBackend(Backend):
    def __init__(self, fifo, **kwargs):
        super().__init__(**kwargs)

        self.fifo = fifo

    def _send_msg(self, msg):
        msglen = len(str(msg))+1  # Include \n

        # Message format: b"<length>\n<message>\n"
        msg = bytearray((str(msglen) + '\n' + str(msg) + '\n').encode('utf-8'))
        with open(self.fifo, 'wb') as f:
            f.write(msg)

    def run(self):
        try: os.mkfifo(self.fifo)
        except FileExistsError as e: pass
        logging.info('Initialized local backend on fifo {}'.format(self.fifo))

        with open(self.fifo, 'rb', 0) as f:
            while True:
                try:
                    msglen = int(f.readline())
                except ValueError as e:
                    time.sleep(0.1)
                    continue

                msg = f.read(msglen-1)
                if not msg: continue

                try:
                    msg = json.loads(msg.decode('utf-8'))
                except Exception as e:
                    logging.exception(e)
                    continue

                logging.debug('Received message: {}'.format(msg))
                self.on_msg(msg)

# vim:sw=4:ts=4:et:

