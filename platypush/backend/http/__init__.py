import asyncio
import datetime
import dateutil.parser
import inspect
import json
import os
import re
import time

from threading import Thread
from multiprocessing import Process
from flask import Flask, abort, jsonify, request as http_request, render_template, send_from_directory
from redis import Redis

from platypush.config import Config
from platypush.message import Message
from platypush.message.event import Event
from platypush.message.event.web.widget import WidgetUpdateEvent
from platypush.message.request import Request

from .. import Backend


class HttpBackend(Backend):
    """ Example interaction with the HTTP backend to make requests:
        $ curl -XPOST -H 'Content-Type: application/json' -H "X-Token: your_token" \
            -d '{"type":"request","target":"nodename","action":"tts.say","args": {"phrase":"This is a test"}}' \
            http://localhost:8008/execute """

    hidden_plugins = {
        'assistant.google'
    }

    def __init__(self, port=8008, websocket_port=8009, disable_websocket=False,
                 redis_queue='platypush_flask_mq', token=None, dashboard={},
                 maps={}, **kwargs):
        super().__init__(**kwargs)

        self.port = port
        self.websocket_port = websocket_port
        self.redis_queue = redis_queue
        self.token = token
        self.dashboard = dashboard
        self.maps = maps
        self.server_proc = None
        self.disable_websocket = disable_websocket
        self.websocket_thread = None
        self.active_websockets = set()
        self.redis = Redis()


    def send_message(self, msg):
        self.logger.warning('Use cURL or any HTTP client to query the HTTP backend')


    def stop(self):
        self.logger.info('Received STOP event on HttpBackend')

        if self.server_proc:
            self.server_proc.terminate()
            self.server_proc.join()


    def notify_web_clients(self, event):
        import websockets

        async def send_event(websocket):
            await websocket.send(str(event))

        loop = asyncio.new_event_loop()

        for websocket in self.active_websockets:
            try:
                loop.run_until_complete(send_event(websocket))
            except websockets.exceptions.ConnectionClosed:
                self.logger.info('Client connection lost')


    def redis_poll(self):
        while not self.should_stop():
            msg = self.redis.blpop(self.redis_queue)
            msg = Message.build(json.loads(msg[1].decode('utf-8')))
            self.bus.post(msg)


    def webserver(self):
        basedir = os.path.dirname(inspect.getfile(self.__class__))
        template_dir = os.path.join(basedir, 'templates')
        static_dir = os.path.join(basedir, 'static')
        app = Flask(__name__, template_folder=template_dir)
        Thread(target=self.redis_poll).start()

        @app.route('/execute', methods=['POST'])
        def execute():
            args = json.loads(http_request.data.decode('utf-8'))
            token = http_request.headers['X-Token'] if 'X-Token' in http_request.headers else None
            if token != self.token: abort(401)

            msg = Message.build(args)
            self.logger.info('Received message on the HTTP backend: {}'.format(msg))

            if isinstance(msg, Request):
                response = msg.execute(async=False)
                self.logger.info('Processing response on the HTTP backend: {}'.format(msg))
                return str(response)
            elif isinstance(msg, Event):
                self.redis.rpush(self.redis_queue, msg)

            return jsonify({ 'status': 'ok' })


        @app.route('/')
        def index():
            configured_plugins = Config.get_plugins()
            enabled_plugins = {}
            hidden_plugins = {}

            for plugin, conf in configured_plugins.items():
                template_file = os.path.join('plugins', plugin + '.html')
                if os.path.isfile(os.path.join(template_dir, template_file)):
                    if plugin in self.hidden_plugins:
                        hidden_plugins[plugin] = conf
                    else:
                        enabled_plugins[plugin] = conf

            return render_template('index.html', plugins=enabled_plugins, hidden_plugins=hidden_plugins,
                                   token=self.token, websocket_port=self.websocket_port)


        @app.route('/widget/<widget>', methods=['POST'])
        def widget_update(widget):
            event = WidgetUpdateEvent(
                widget=widget, **(json.loads(http_request.data.decode('utf-8'))))

            self.redis.rpush(self.redis_queue, event)
            return jsonify({ 'status': 'ok' })

        @app.route('/static/<path>', methods=['GET'])
        def static_path(path):
            return send_from_directory(static_dir, filename)

        @app.route('/dashboard', methods=['GET'])
        def dashboard():
            return render_template('dashboard.html', config=self.dashboard, utils=HttpUtils,
                                   token=self.token, websocket_port=self.websocket_port)

        @app.route('/map', methods=['GET'])
        def map():
            """
            Query parameters:
                start -- Map timeline start timestamp
                end   -- Map timeline end timestamp
                zoom  -- Between 1-20. Set it if you want to override the
                    Google's API auto-zoom. You may have to set it if you are
                    trying to embed the map into an iframe

            Supported values for `start` and `end`:
                - now
                - yesterday
                - -30s (it means '30 seconds ago')
                - -10m (it means '10 minutes ago')
                - -24h (it means '24 hours ago')
                - -7d  (it means '7 days ago')
                - 2018-06-04T17:39:22.742Z (ISO strings)

            Default: start=yesterday, end=now
            """

            def parse_time(time_string):
                if not time_string:
                    return None

                now = datetime.datetime.now()

                if time_string == 'now':
                    return now.isoformat()
                if time_string == 'yesterday':
                    return (now - datetime.timedelta(days=1)).isoformat()

                try:
                    return dateutil.parser.parse(time_string).isoformat()
                except ValueError:
                    pass

                m = re.match('([-+]?)(\d+)([dhms])', time_string)
                if not m:
                    raise RuntimeError('Invalid time interval string representation: "{}"'.
                                    format(time_string))

                time_delta = (-1 if m.group(1) == '-' else 1) * int(m.group(2))
                time_unit = m.group(3)

                if time_unit == 'd':
                    params = { 'days': time_delta }
                elif time_unit == 'h':
                    params = { 'hours': time_delta }
                elif time_unit == 'm':
                    params = { 'minutes': time_delta }
                elif time_unit == 's':
                    params = { 'seconds': time_delta }

                return (now + datetime.timedelta(**params)).isoformat()

            try:
                api_key = self.maps['api_key']
            except KeyError:
                raise RuntimeError('Google Maps api_key not set in the maps configuration')

            start = parse_time(http_request.args.get('start', default='yesterday'))
            end = parse_time(http_request.args.get('end', default='now'))
            zoom = http_request.args.get('zoom', default=None)

            return render_template('map.html', config=self.maps,
                                   utils=HttpUtils, start=start, end=end,
                                   zoom=zoom, token=self.token, api_key=api_key,
                                   websocket_port=self.websocket_port)

        return app


    def websocket(self):
        import websockets

        async def register_websocket(websocket, path):
            self.logger.info('New websocket connection from {}'.format(websocket.remote_address[0]))
            self.active_websockets.add(websocket)

            try:
                await websocket.recv()
            except websockets.exceptions.ConnectionClosed:
                self.logger.info('Websocket client {} closed connection'.format(websocket.remote_address[0]))
                self.active_websockets.remove(websocket)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            websockets.serve(register_websocket, '0.0.0.0', self.websocket_port))
        loop.run_forever()


    def run(self):
        super().run()
        self.logger.info('Initialized HTTP backend on port {}'.format(self.port))

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


class HttpUtils(object):
    @staticmethod
    def widget_columns_to_html_class(columns):
        if not isinstance(columns, int):
            raise RuntimeError('columns should be a number, got "{}"'.format(columns))

        if columns == 1:
            return 'one column'
        elif columns == 2:
            return 'two columns'
        elif columns == 3:
            return 'three columns'
        elif columns == 4:
            return 'four columns'
        elif columns == 5:
            return 'five columns'
        elif columns == 6:
            return 'six columns'
        elif columns == 7:
            return 'seven columns'
        elif columns == 8:
            return 'eight columns'
        elif columns == 9:
            return 'nine columns'
        elif columns == 10:
            return 'ten columns'
        elif columns == 11:
            return 'eleven columns'
        elif columns == 12:
            return 'twelve columns'
        else:
            raise RuntimeError('Constraint violation: should be 1 <= columns <= 12, ' +
                               'got columns={}'.format(columns))

    @staticmethod
    def search_directory(directory, *extensions, recursive=False):
        files = []

        if recursive:
            for root, subdirs, files in os.walk(directory):
                for file in files:
                    if not extensions or os.path.splitext(file)[1].lower() in extensions:
                        files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                if not extensions or os.path.splitext(file)[1].lower() in extensions:
                    files.append(os.path.join(directory, file))

        return files

    @classmethod
    def search_web_directory(cls, directory, *extensions):
        directory = re.sub('^/+', '', directory)
        basedir = os.path.dirname(inspect.getfile(cls))
        results = cls.search_directory(os.path.join(basedir, directory), *extensions)
        return [item[len(basedir):] for item in results]

    @classmethod
    def to_json(cls, data):
        return json.dumps(data)

    @classmethod
    def from_json(cls, data):
        return json.loads(data)


# vim:sw=4:ts=4:et:

