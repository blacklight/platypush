import asyncio
import inspect
import logging
import json
import os
import time

from threading import Thread
from multiprocessing import Process
from flask import Flask, abort, jsonify, request, render_template, send_from_directory

from platypush.config import Config
from platypush.message import Message
from platypush.message.event import Event
from platypush.message.request import Request

from .. import Backend


class HttpBackend(Backend):
    """ Example interaction with the HTTP backend to make requests:
        $ curl -XPOST -H 'Content-Type: application/json' -H "X-Token: your_token" \
            -d '{"type":"request","target":"nodename","action":"tts.say","args": {"phrase":"This is a test"}}' \
            http://localhost:8008/execute """

    def __init__(self, port=8008, websocket_port=8009, disable_websocket=False,
                 token=None, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.websocket_port = websocket_port
        self.token = token
        self.server_proc = None
        self.disable_websocket = disable_websocket
        self.websocket_thread = None
        self.active_websockets = set()


    def send_message(self, msg):
        logging.warning('Use cURL or any HTTP client to query the HTTP backend')


    def stop(self):
        logging.info('Received STOP event on HttpBackend')

        if self.server_proc:
            self.server_proc.terminate()
            self.server_proc.join()


    def notify_web_clients(self, event):
        import websockets

        async def send_event(websocket):
            await websocket.send(str(event))

        loop = asyncio.new_event_loop()
        active_websockets = set()

        for websocket in self.active_websockets:
            try:
                loop.run_until_complete(send_event(websocket))
                active_websockets.add(websocket)
            except websockets.exceptions.ConnectionClosed:
                logging.info('Client connection lost')

        self.active_websockets = active_websockets


    def webserver(self):
        basedir = os.path.dirname(inspect.getfile(self.__class__))
        template_dir = os.path.join(basedir, 'templates')
        static_dir = os.path.join(basedir, 'static')
        app = Flask(__name__, template_folder=template_dir)

        @app.route('/execute', methods=['POST'])
        def execute():
            args = json.loads(request.data.decode('utf-8'))
            token = request.headers['X-Token'] if 'X-Token' in request.headers else None
            if token != self.token: abort(401)

            msg = Message.build(args)
            logging.info('Received message on the HTTP backend: {}'.format(msg))

            if isinstance(msg, Request):
                response = msg.execute(async=False)
                logging.info('Processing response on the HTTP backend: {}'.format(msg))
                return str(response)
            elif isinstance(msg, Event):
                self.bus.post(msg)

            return jsonify({ 'status': 'ok' })


        @app.route('/')
        def index():
            configured_plugins = Config.get_plugins()
            enabled_plugins = {}

            for plugin, conf in configured_plugins.items():
                template_file = os.path.join('plugins', plugin + '.html')
                if os.path.isfile(os.path.join(template_dir, template_file)):
                    enabled_plugins[plugin] = conf

            return render_template('index.html', plugins=enabled_plugins,
                                   token=self.token, websocket_port=self.websocket_port)


        @app.route('/static/<path>')
        def static_path(path):
            return send_from_directory(static_dir, filename)

        return app


    def websocket(self):
        import websockets

        async def register_websocket(websocket, path):
            logging.info('New websocket connection from {}'.format(websocket.remote_address[0]))
            self.active_websockets.add(websocket)

            while True:
                try:
                    waiter = await websocket.ping()
                    await asyncio.wait_for(waiter, timeout=5)
                except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed) as e:
                    logging.info('Client {} closed connection'.format(websocket.remote_address[0]))
                    self.active_websockets.remove(websocket)
                    break

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            websockets.serve(register_websocket, '0.0.0.0', self.websocket_port))
        loop.run_forever()


    def run(self):
        super().run()
        logging.info('Initialized HTTP backend on port {}'.format(self.port))

        webserver = self.webserver()
        self.server_proc = Process(target=webserver.run, kwargs={
            'debug':True, 'host':'0.0.0.0', 'port':self.port, 'use_reloader':False
        })

        time.sleep(1)

        self.server_proc.start()

        if not self.disable_websocket:
            self.websocket_thread = Thread(target=self.websocket)
            self.websocket_thread.start()

        self.server_proc.join()


# vim:sw=4:ts=4:et:

