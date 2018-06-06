import json
import os
import time
import threading

from .. import Backend

from platypush.message import Message
from platypush.message.event import StopEvent
from platypush.message.request import Request
from platypush.message.response import Response


class LocalBackend(Backend):
    """
    Sends and receive messages on two distinct local FIFOs, one for
    the requests and one for the responses.

    You can use this backend either to send local commands to push through
    Pusher (or any other script), or debug. You can even send command on the
    command line and read the responses in this way:

    # Send the request. Remember: the JSON must be all on one line.
    $ cat <<EOF > /tmp/platypush-requests.fifo
	{"type": "request", "target": "node_name", "action": "shell.exec", "args": {"cmd":"echo ping"}, "origin": "node_name", "id": "put_an_id_here"}
	EOF
	$ cat /tmp/platypush-responses.fifo
	ping
	$
    """

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


    def run(self):
        super().run()
        self.logger.info('Initialized local backend on {} and {}'.
                     format(self.request_fifo, self.response_fifo))

        while not self.should_stop():
            try:
                msg = self._get_next_message()
                if not msg: continue
            except Exception as e:
                self.logger.exception(e)
                time.sleep(0.2)
                continue

            self.logger.debug('Received message on the local backend: {}, thread_id: '.format(msg, self.thread_id))

            if self.should_stop(): break
            self.on_message(msg)


# vim:sw=4:ts=4:et:

