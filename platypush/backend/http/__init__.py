import logging
import json

from multiprocessing import Process
from flask import Flask, abort, jsonify, request

from platypush.message import Message
from platypush.message.request import Request

from .. import Backend


class HttpBackend(Backend):
    """ Example interaction with the HTTP backend to make requests:
        $ curl -XPOST \
            -d 'msg={"type":"request","target":"volta","action":"tts.say","args": {"phrase":"This is a test"}}' \
            http://localhost:8008 """

    def __init__(self, port=8008, token=None, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.token = token


    def send_message(self, msg):
        raise NotImplementedError('Use cURL or any HTTP client to query the HTTP backend')


    def _start_server(self):
        def app_main():
            app = Flask(__name__)

            @app.route('/', methods=['POST'])
            def index():
                args = { k:v for (k,v) in request.form.items() }

                if self.token:
                    if 'token' not in args or args['token'] != self.token:
                        abort(401)

                if 'msg' not in args:
                    abort(400)

                msg = Message.build(args['msg'])
                logging.debug('Received message on HTTP backend: {}'.format(msg))

                if isinstance(msg, Request):
                    response = msg.execute(async=False)
                    return str(response)

                return jsonify({ 'status': 'ok' })

            app.run(debug=True, host='0.0.0.0', port=self.port)
            logging.info('Initialized HTTP backend on port {}'.format(self.port))

        return app_main

    def run(self):
        super().run()
        self.server_proc = Process(target=self._start_server())
        self.server_proc.start()
        self.server_proc.join()


# vim:sw=4:ts=4:et:

