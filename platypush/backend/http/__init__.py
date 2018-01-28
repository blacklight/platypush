import logging
import json
import time

from multiprocessing import Process
from flask import Flask, abort, jsonify, request

from platypush.config import Config
from platypush.message import Message
from platypush.message.request import Request

from .. import Backend


class HttpBackend(Backend):
    """ Example interaction with the HTTP backend to make requests:
        $ curl -XPOST -H 'Content-Type: application/json' -H "X-Token: your_token" \
            -d '{"type":"request","target":"nodename","action":"tts.say","args": {"phrase":"This is a test"}}' \
            http://localhost:8008/execute """

    def __init__(self, port=8008, token=None, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.token = token
        self.server_proc = None


    def send_message(self, msg):
        logging.warning('Use cURL or any HTTP client to query the HTTP backend')


    def stop(self):
        logging.info('Received STOP event on HttpBackend')
        if self.server_proc:
            self.server_proc.terminate()
            self.server_proc.join()


    def run(self):
        super().run()

        app = Flask(__name__)

        @app.route('/execute', methods=['POST'])
        def index():
            args = json.loads(request.data.decode('utf-8'))
            token = request.headers['X-Token'] if 'X-Token' in request.headers else None
            if token != self.token: abort(401)

            msg = Message.build(args)
            logging.info('Received message on the HTTP backend: {}'.format(msg))

            if isinstance(msg, Request):
                response = msg.execute(async=False)
                logging.info('Processing response on the HTTP backend: {}'.format(msg))
                return str(response)

            return jsonify({ 'status': 'ok' })

        logging.info('Initialized HTTP backend on port {}'.format(self.port))

        self.server_proc = Process(target=app.run, kwargs={
            'debug':True, 'host':'0.0.0.0', 'port':self.port, 'use_reloader':False
        })

        time.sleep(1)

        self.server_proc.start()
        self.server_proc.join()


# vim:sw=4:ts=4:et:

