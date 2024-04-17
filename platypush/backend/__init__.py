import logging
import re
import socket
import time

from threading import Thread, Event as ThreadEvent, get_ident
from typing import Optional, Dict

from platypush import __version__
from platypush.bus import Bus
from platypush.common import ExtensionWithManifest
from platypush.config import Config
from platypush.context import get_backend
from platypush.event import EventGenerator
from platypush.message import Message
from platypush.message.event import Event
from platypush.message.event.zeroconf import (
    ZeroconfServiceAddedEvent,
    ZeroconfServiceRemovedEvent,
)
from platypush.message.request import Request
from platypush.message.response import Response
from platypush.utils import (
    clear_timeout,
    get_backend_name_by_class,
    get_redis,
    get_redis_queue_name_by_message,
    get_remaining_timeout,
    set_timeout,
)


class Backend(Thread, EventGenerator, ExtensionWithManifest):
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

    def __init__(
        self, bus: Optional[Bus] = None, poll_seconds: Optional[float] = None, **kwargs
    ):
        """
        :param bus: Reference to the bus object to be used in the backend
        :param poll_seconds: If the backend implements a ``loop`` method, this parameter expresses how often the
            loop should run in seconds.
        :param kwargs: Key-value configuration for the backend
        """

        self._thread_name = self.__class__.__name__
        EventGenerator.__init__(self)
        ExtensionWithManifest.__init__(self)
        Thread.__init__(self, name=self._thread_name, daemon=True)

        # If no bus is specified, create an internal queue where
        # the received messages will be pushed
        self.bus = bus or Bus()
        self.poll_seconds = float(poll_seconds) if poll_seconds else None
        self.device_id = Config.get('device_id')
        self.thread_id = None
        self._stop_event = ThreadEvent()
        self._stop_thread: Optional[Thread] = None
        self._kwargs = kwargs
        self.logger = logging.getLogger(
            'platypush:backend:' + get_backend_name_by_class(self.__class__)
        )
        self.zeroconf = None
        self.zeroconf_info = None

        # Internal-only, we set the request context on a backend if that
        # backend is intended to react for a response to a specific request
        self._request_context = kwargs['_req_ctx'] if '_req_ctx' in kwargs else None

        if 'logging' in kwargs:
            self.logger.setLevel(getattr(logging, kwargs['logging'].upper()))

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
        if msg is None:
            return

        if not getattr(msg, 'target', None) or msg.target != self.device_id:
            return  # Not for me

        self.logger.debug(
            'Message received on the %s backend: %s', self.__class__.__name__, msg
        )

        if self._is_expected_response(msg):
            # Expected response, trigger the response handler
            clear_timeout()
            if self._request_context:
                # pylint: disable=unsubscriptable-object
                self._request_context['on_response'](msg)

            self.stop()
            return

        msg.backend = self  # Augment message to be able to process responses
        self.bus.post(msg)

    def _is_expected_response(self, msg):
        """
        Internal only - returns true if we are expecting for a response and msg
        is that response.
        """

        # pylint: disable=unsubscriptable-object
        return (
            self._request_context
            and isinstance(msg, Response)
            and msg.id == self._request_context['request'].id
        )

    def _get_backend_config(self):
        config_name = (
            'backend.' + self.__class__.__name__.split('Backend', maxsplit=1)[0].lower()
        )
        return Config.get(config_name) or {}

    def _setup_response_handler(self, request, on_response, response_timeout):
        def _timeout_hndl():
            raise RuntimeError(
                f'Timed out while waiting for a response from {request.target}'
            )

        req_ctx = {
            'request': request,
            'on_response': on_response,
            'response_timeout': response_timeout,
        }

        resp_backend = self.__class__(
            bus=self.bus, _req_ctx=req_ctx, **self._get_backend_config(), **self._kwargs
        )

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

    def send_request(
        self,
        request,
        on_response=None,
        response_timeout=_default_response_timeout,
        **kwargs,
    ):
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

    def send_message(self, msg, queue_name=None, **_):
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
            self.logger.warning(
                (
                    "Backend %s does not implement send_message "
                    "and the fallback Redis backend isn't configured"
                ),
                self.__class__.__name__,
            )
            return

        redis.send_message(msg, queue_name=queue_name)

    def run(self):
        """Starts the backend thread. To be implemented in the derived classes if the loop method isn't defined."""
        self.thread_id = get_ident()
        if not callable(self.loop):
            return

        while not self.should_stop():
            try:
                with self:
                    has_error = False

                    while not self.should_stop() and not has_error:
                        try:
                            # pylint: disable=not-callable
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
                self.logger.error(
                    '%s initialization error: %s', self.__class__.__name__, e
                )
                self.logger.exception(e)
                time.sleep(self.poll_seconds or 5)

    def __enter__(self):
        """Invoked when the backend is initialized, if the main logic is within a ``loop()`` function"""
        self.logger.info('Initialized backend %s', self.__class__.__name__)

    def __exit__(self, *_, **__):
        """Invoked when the backend is terminated, if the main logic is within a ``loop()`` function"""
        self.on_stop()
        self.logger.info('Terminated backend %s', self.__class__.__name__)

    def on_stop(self):
        """Callback invoked when the process stops"""

    def stop(self):
        """Stops the backend thread by sending a STOP event on its bus"""

        def _async_stop():
            self._stop_event.set()
            self.unregister_service()
            self.on_stop()
            self._stop_thread = None

        if not (self._stop_thread and self._stop_thread.is_alive()):
            self._stop_thread = Thread(target=_async_stop)
            self._stop_thread.start()

    def should_stop(self):
        """
        :return: True if the backend thread should be stopped, False otherwise.
        """
        return self._stop_event.is_set()

    def wait_stop(self, timeout=None) -> bool:
        """
        Waits for the backend thread to stop.

        :param timeout: The maximum time to wait for the backend thread to stop (default: None)
        :return: True if the backend thread has stopped, False otherwise.
        """
        start = time.time()

        if self._stop_thread:
            try:
                self._stop_thread.join(
                    get_remaining_timeout(timeout=timeout, start=start)
                )
            except AttributeError:
                pass

        return self._stop_event.wait(
            get_remaining_timeout(timeout=timeout, start=start)
        )

    def get_message_response(self, msg):
        queue = get_redis_queue_name_by_message(msg)
        if not queue:
            self.logger.warning('No response queue configured for the message')
            return None

        try:
            redis = get_redis()
            response = redis.blpop(queue, timeout=60)
            if response and len(response) > 1:
                response = Message.build(response[1])
            else:
                response = None

            return response
        except Exception as e:
            self.logger.error('Error while processing response to %s: %s', msg, e)

        return None

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

    def register_service(
        self,
        port: Optional[int] = None,
        name: Optional[str] = None,
        srv_type: Optional[str] = None,
        srv_name: Optional[str] = None,
        udp: bool = False,
        properties: Optional[Dict] = None,
    ):
        """
        Initialize the Zeroconf service configuration for this backend.

        :param port: Service listen port (default: the backend ``port`` attribute if available, or ``None``).
        :param name: Service short name (default: backend name).
        :param srv_type: Service type (default: ``_platypush-{name}._{proto}.local.``).
        :param srv_name: Full service name (default: ``{hostname or device_id}.{type}``).
        :param udp: Set to True if this is a UDP service.
        :param properties: Extra properties to be passed on the service. Default:

            .. code-block:: json

                {
                    "name": "Platypush",
                    "vendor": "Platypush",
                    "version": "{platypush_version}"
                }

        """
        try:
            from zeroconf import ServiceInfo, Zeroconf
            from platypush.plugins.zeroconf import ZeroconfListener
        except ImportError:
            self.logger.warning(
                'zeroconf package not available, service discovery will be disabled.'
            )
            return

        if self.zeroconf:
            self.logger.info(
                'Zeroconf service already registered for %s, removing the previous instance',
                self.__class__.__name__,
            )
            self.unregister_service()

        self.zeroconf = Zeroconf()
        srv_desc = {
            'name': 'Platypush',
            'vendor': 'Platypush',
            'version': __version__,
            **(properties or {}),
        }

        name = name or re.sub(r'Backend$', '', self.__class__.__name__).lower()
        srv_type = srv_type or f'_platypush-{name}._{"udp" if udp else "tcp"}.local.'
        srv_name = srv_name or f'{self.device_id}.{srv_type}'
        srv_port = port if port else getattr(self, 'port', None)
        self.zeroconf_info = ServiceInfo(
            srv_type,
            srv_name,
            addresses=[socket.inet_aton(self._get_ip())],
            port=srv_port,
            weight=0,
            priority=0,
            properties=srv_desc,
        )

        if not self.zeroconf_info:
            self.logger.warning('Could not register Zeroconf service')
            return

        self.zeroconf.register_service(self.zeroconf_info)
        self.bus.post(
            ZeroconfServiceAddedEvent(
                service_type=srv_type,
                service_name=srv_name,
                service_info=ZeroconfListener.parse_service_info(self.zeroconf_info),
            )
        )

    def unregister_service(self):
        """
        Unregister the Zeroconf service configuration if available.
        """
        from redis import exceptions

        if self.zeroconf and self.zeroconf_info:
            try:
                self.zeroconf.unregister_service(self.zeroconf_info)
            except Exception as e:
                self.logger.warning(
                    'Could not register Zeroconf service %s: %s: %s',
                    self.zeroconf_info.name,
                    type(e).__name__,
                    e,
                )

            if self.zeroconf:
                try:
                    self.zeroconf.close()
                except TimeoutError:
                    pass

            try:
                if self.zeroconf_info:
                    self.bus.post(
                        ZeroconfServiceRemovedEvent(
                            service_type=self.zeroconf_info.type,
                            service_name=self.zeroconf_info.name,
                        )
                    )
                else:
                    self.bus.post(
                        ZeroconfServiceRemovedEvent(
                            service_type=None, service_name=None
                        )
                    )
            except exceptions.ConnectionError:
                pass

            self.zeroconf_info = None
            self.zeroconf = None


# vim:sw=4:ts=4:et:
