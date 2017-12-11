import logging
import json
import os
import time

from .. import Backend

class LocalBackend(Backend):
    def _init(self, fifo):
        self.fifo = fifo
        try: os.mkfifo(self.fifo)
        except FileExistsError as e: pass
        logging.info('Initialized local backend on fifo {}'.format(self.fifo))

    def send_msg(self, msg):
        if isinstance(msg, dict):
            msg = json.dumps(msg)
        if not isinstance(msg, str):
            msg = json.dumps(msg)
            raise RuntimeError('Invalid non-JSON message')

        msglen = len(msg)+1  # Include \n
        msg = bytearray((str(msglen) + '\n' + msg + '\n').encode('utf-8'))
        with open(self.fifo, 'wb') as f:
            f.write(msg)

    def run(self):
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

