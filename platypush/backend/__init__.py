"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
.. license: MIT
"""

import logging
import re
import socket
import threading
import time

from threading import Thread
from typing import Optional

from platypush.bus import Bus
from platypush.config import Config
from platypush.context import get_backend
from platypush.message.event.zeroconf import ZeroconfServiceAddedEvent, ZeroconfServiceRemovedEvent
from platypush.utils import set_timeout, clear_timeout, \
    get_redis_queue_name_by_message, set_thread_name, get_backend_name_by_class

from platypush import __version__
from platypush.event import EventGenerator
from platypush.message import Message
from platypush.message.event import Event, StopEvent
from platypush.message.request import Request
from platypush.message.response import Response


class Backend(Thread, EventGenerator):
    """
    Parent class for backends.

    A backend is basically a thread that checks for new events on some channel
    (e.g. a network socket, a queue, some new entries on an API endpoint or an
    RSS feed, a voice command through an assistant, a new measure from a sensor
    etc.) and propagates event messages to the main application bus whenever a
    new event happens. You can then build whichever type of custom logic you
    want on such events.
    """

    _default_response_timeout = 5

    # Loop function, can be implemented by derived classes
    loop = None

    def __init__(self, bus: Optional[Bus] = None, poll_seconds: Optional[float] = None, **kwargs):
        """
        :param bus: Reference to the bus object to be used in the backend
        :param poll_seconds: If the backend implements a ``loop`` method, this parameter expresses how often the
            loop should run in seconds.
        :param kwargs: Key-value configuration for the backend
        """

        self._thread_name = self.__class__.__name__
        EventGenerator.__init__(self)
        Thread.__init__(self, name=self._thread_name, daemon=True)

        # If no bus is specified, create an internal queue where
        # the received messages will be pushed
        self.bus = bus or Bus()
        self.poll_seconds = float(poll_seconds) if poll_seconds else None
        self.device_id = Config.get('device_id')
        self.thread_id = None
        self._should_stop = False
        self._stop_event = threading.Event()
        self._kwargs = kwargs
        self.logger = logging.getLogger('platypush:backend:' + get_backend_name_by_class(self.__class__))
        self.zeroconf = None
        self.zeroconf_info = None

        # Internal-only, we set the request context on a backend if that
        # backend is intended to react for a response to a specific request
        self._request_context = kwargs['_req_ctx'] if '_req_ctx' in kwargs \
            else None

        if 'logging' in kwargs:
            self.logger.setLevel(getattr(logging, kwargs.get('logging').upper()))

    def on_message(self, msg):
        """
        Callback when a message is received on the backend.
        It parses and posts the message on the main bus.
        It should be called by the derived classes whenever
        a new message should be processed.

        :param msg: Received message.  It can be either a key-value dictionary, a platypush.message.Message object,
            or a string/byte UTF-8 encoded string
        """

        msg = Message.build(msg)

        if not getattr(msg, 'target') or msg.target != self.device_id:
            return  # Not for me

        self.logger.debug('Message received on the {} backend: {}'.format(
            self.__class__.__name__, msg))

        if self._is_expected_response(msg):
            # Expected response, trigger the response handler
            clear_timeout()
            self._request_context['on_response'](msg)
            self.stop()
            return

        if isinstance(msg, StopEvent) and msg.targets_me():
            self.logger.info('Received STOP event on {}'.format(self.__class__.__name__))
            self._should_stop = True
        else:
            msg.backend = self   # Augment message to be able to process responses
            self.bus.post(msg)

    def _is_expected_response(self, msg):
        """ Internal only - returns true if we are expecting for a response
            and msg is that response """

        return self._request_context \
            and isinstance(msg, Response) \
            and msg.id == self._request_context['request'].id

    def _get_backend_config(self):
        config_name = 'backend.' + self.__class__.__name__.split('Backend')[0].lower()
        return Config.get(config_name)

    def _setup_response_handler(self, request, on_response, response_timeout):
        def _timeout_hndl():
            raise RuntimeError('Timed out while waiting for a response from {}'.
                               format(request.target))

        req_ctx = {
            'request': request,
            'on_response': on_response,
            'response_timeout': response_timeout,
        }

        resp_backend = self.__class__(bus=self.bus, _req_ctx=req_ctx,
                                      **self._get_backend_config(), **self._kwargs)

        # Set the response timeout
        if response_timeout:
            set_timeout(seconds=response_timeout, on_timeout=_timeout_hndl)

        resp_backend.start()

    def send_event(self, event, **kwargs):
        """
        Send an event message on the backend.

        :param event: Event to send. It can be a dict, a string/bytes UTF-8 JSON, or a platypush.message.event.Event
            object.
        """

        event = Event.build(event)
        assert isinstance(event, Event)

        event.origin = self.device_id
        if not hasattr(event, 'target'):
            event.target = self.device_id

        self.send_message(event, **kwargs)

    def send_request(self, request, on_response=None,
                     response_timeout=_default_response_timeout, **kwargs):
        """
        Send a request message on the backend.

        :param request: The request, either a dict, a string/bytes UTF-8 JSON, or a platypush.message.request.Request
            object.

        :param on_response: Optional callback that will be called when a response is received. If set, this method will
            synchronously wait for a response before exiting.
        :type on_response: function

        :param response_timeout: If on_response is set, the backend will raise an exception if the response isn't
            received within this number of seconds (default: None)
        :type response_timeout: float
        """

        request = Request.build(request)
        assert isinstance(request, Request)

        request.origin = self.device_id

        if on_response and response_timeout != 0:
            self._setup_response_handler(request, on_response, response_timeout)

        self.send_message(request, **kwargs)

    def send_response(self, response, request, **kwargs):
        """
        Send a response message on the backend.

        :param response: The response, either a dict, a string/bytes UTF-8 JSON, or a
            :class:`platypush.message.response.Response` object.
        :param request: Associated request, used to set the response parameters that will link them
        """

        assert isinstance(response, Response)
        assert isinstance(request, Request)

        self.send_message(response, **kwargs)

    def send_message(self, msg, queue_name=None, **kwargs):
        """
        Sends a platypush.message.Message to a node.
        To be implemented in the derived classes. By default, if the Redis
        backend is configured then it will try to deliver the message to
        other consumers through the configured Redis main queue.

        :param msg: The message to send
        :param queue_name: Send the message on a specific queue (default: the queue_name configured on the Redis
            backend)
        """

        try:
            redis = get_backend('redis')
            if not redis:
                raise KeyError()
        except KeyError:
            self.logger.warning("Backend {} does not implement send_message " +
                                "and the fallback Redis backend isn't configured")
            return

        redis.send_message(msg, queue_name=queue_name)

    def run(self):
        """ Starts the backend thread. To be implemented in the derived classes if the loop method isn't defined. """
        self.thread_id = threading.get_ident()
        set_thread_name(self._thread_name)
        if not callable(self.loop):
            return

        while not self.should_stop():
            try:
                with self:
                    has_error = False

                    while not self.should_stop() and not has_error:
                        try:
                            self.loop()
                        except Exception as e:
                            has_error = True
                            self.logger.error(str(e))
                            self.logger.exception(e)
                        finally:
                            if self.poll_seconds:
                                time.sleep(self.poll_seconds)
                            elif has_error:
                                time.sleep(5)
            except Exception as e:
                self.logger.error('{} initialization error: {}'.format(self.__class__.__name__, str(e)))
                self.logger.exception(e)
                time.sleep(self.poll_seconds or 5)

    def __enter__(self):
        """ Invoked when the backend is initialized, if the main logic is within a ``loop()`` function """
        self.logger.info('Initialized backend {}'.format(self.__class__.__name__))

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Invoked when the backend is terminated, if the main logic is within a ``loop()`` function """
        self.on_stop()
        self.logger.info('Terminated backend {}'.format(self.__class__.__name__))

    def on_stop(self):
        """ Callback invoked when the process stops """
        self.unregister_service()

    def stop(self):
        """ Stops the backend thread by sending a STOP event on its bus """
        def _async_stop():
            evt = StopEvent(target=self.device_id, origin=self.device_id,
                            thread_id=self.thread_id)

            self.send_message(evt)
            self._stop_event.set()
            self.on_stop()

        Thread(target=_async_stop).start()

    def should_stop(self):
        return self._should_stop

    def wait_stop(self, timeout=None) -> bool:
        return self._stop_event.wait(timeout)

    def _get_redis(self):
        import redis

        redis_backend = get_backend('redis')
        if not redis_backend:
            self.logger.warning('Redis backend not configured - some ' +
                                'web server features may not be working properly')
            redis_args = {}
        else:
            redis_args = redis_backend.redis_args

        redis = redis.Redis(**redis_args)
        return redis

    def get_message_response(self, msg):
        try:
            redis = self._get_redis()
            response = redis.blpop(get_redis_queue_name_by_message(msg), timeout=60)
            if response and len(response) > 1:
                response = Message.build(response[1])
            else:
                response = None

            return response
        except Exception as e:
            self.logger.error('Error while processing response to {}: {}'.format(msg, str(e)))

    @staticmethod
    def _get_ip() -> str:
        """
        Get the IP address of the machine.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        addr = s.getsockname()[0]
        s.close()
        return addr

    def register_service(self, port: Optional[int] = None, name: Optional[str] = None, udp: bool = False):
        """
        Initialize the Zeroconf service configuration for this backend.
        """
        try:
            from zeroconf import ServiceInfo, Zeroconf
            from platypush.plugins.zeroconf import ZeroconfListener
        except ImportError:
            self.logger.warning('zeroconf package not available, service discovery will be disabled.')
            return

        self.zeroconf = Zeroconf()
        srv_desc = {
            'name': 'Platypush',
            'vendor': 'Platypush',
            'version': __version__,
        }

        name = name or re.sub(r'Backend$', '', self.__class__.__name__).lower()
        srv_type = '_platypush-{name}._{proto}.local.'.format(name=name, proto='udp' if udp else 'tcp')
        srv_name = '{host}.{type}'.format(host=self.device_id, type=srv_type)

        if port:
            srv_port = port
        else:
            srv_port = self.port if hasattr(self, 'port') else None

        self.zeroconf_info = ServiceInfo(srv_type, srv_name,
                                         addresses=[socket.inet_aton(self._get_ip())],
                                         port=srv_port,
                                         weight=0,
                                         priority=0,
                                         properties=srv_desc)

        self.zeroconf.register_service(self.zeroconf_info)
        self.bus.post(ZeroconfServiceAddedEvent(service_type=srv_type, service_name=srv_name,
                                                service_info=ZeroconfListener.parse_service_info(self.zeroconf_info)))

    def unregister_service(self):
        """
        Unregister the Zeroconf service configuration if available.
        """
        if self.zeroconf and self.zeroconf_info:
            self.zeroconf.unregister_service(self.zeroconf_info)
            if self.zeroconf:
                self.zeroconf.close()

            if self.zeroconf_info:
                self.bus.post(ZeroconfServiceRemovedEvent(service_type=self.zeroconf_info.type,
                                                          service_name=self.zeroconf_info.name))
            else:
                self.bus.post(ZeroconfServiceRemovedEvent(service_type=None, service_name=None))

            self.zeroconf_info = None
            self.zeroconf = None


# vim:sw=4:ts=4:et:
