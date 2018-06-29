import importlib
import logging
import sys
import threading

from threading import Thread

from platypush.bus import Bus
from platypush.config import Config
from platypush.context import get_backend
from platypush.utils import get_message_class_by_type, set_timeout, clear_timeout
from platypush.message import Message
from platypush.message.event import Event, StopEvent
from platypush.message.request import Request
from platypush.message.response import Response


class Backend(Thread):
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

    def __init__(self, bus=None, **kwargs):
        """
        :param bus: Reference to the bus object to be used in the backend
        :type bus: platypush.bus.Bus

        :param kwargs: Key-value configuration for the backend
        :type kwargs: dict
        """

        # If no bus is specified, create an internal queue where
        # the received messages will be pushed
        self.bus = bus or Bus()
        self.device_id = Config.get('device_id')
        self.thread_id = None
        self._stop = False
        self._kwargs = kwargs
        self.logger = logging.getLogger(self.__class__.__name__)

        # Internal-only, we set the request context on a backend if that
        # backend is intended to react for a response to a specific request
        self._request_context = kwargs['_req_ctx'] if '_req_ctx' in kwargs \
            else None

        if 'logging' in kwargs:
            self.logger.setLevel(getattr(logging, kwargs['logging'].upper()))

        Thread.__init__(self)


    def on_message(self, msg):
        """
        Callback when a message is received on the backend.
        It parses and posts the message on the main bus.
        It should be called by the derived classes whenever
        a new message should be processed.

        :param msg: Received message.  It can be either a key-value dictionary, a platypush.message.Message object, or a string/byte UTF-8 encoded string
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
            self._stop = True
        else:
            msg.backend = self   # Augment message to be able to process responses
            self.bus.post(msg)


    def _is_expected_response(self, msg):
        """ Internal only - returns true if we are expecting for a response
            and msg is that response """

        return  self._request_context \
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

        :param event: Event to send. It can be a dict, a string/bytes UTF-8 JSON, or a platypush.message.event.Event object.
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

        :param request: The request, either a dict, a string/bytes UTF-8 JSON, or a platypush.message.request.Request object.

        :param on_response: Optional callback that will be called when a response is received. If set, this method will synchronously wait for a response before exiting.
        :type on_response: function

        :param response_timeout: If on_response is set, the backend will raise an exception if the response isn't received within this number of seconds (default: None)
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

        :param response: The response, either a dict, a string/bytes UTF-8 JSON, or a platypush.message.response.Response object
        :param request: Associated request, used to set the response parameters that will link them
        """

        response = Response.build(response)
        assert isinstance(response, Response)
        assert isinstance(request, Request)

        response.id = request.id
        response.target = request.origin
        response.origin = self.device_id

        self.send_message(response, **kwargs)


    def send_message(self, msg, queue_name=None, **kwargs):
        """
        Sends a platypush.message.Message to a node.
        To be implemented in the derived classes. By default, if the Redis
        backend is configured then it will try to deliver the message to
        other consumers through the configured Redis main queue.

        :param msg: The message to send
        :param queue_name: Send the message on a specific queue (default: the queue_name configured on the Redis backend)
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
        """ Starts the backend thread. To be implemented in the derived classes """
        self.thread_id = threading.get_ident()

    def on_stop(self):
        """ Callback invoked when the process stops """
        pass

    def stop(self):
        """ Stops the backend thread by sending a STOP event on its bus """
        def _async_stop():
            evt = StopEvent(target=self.device_id, origin=self.device_id,
                            thread_id=self.thread_id)

            self.send_message(evt)
            self.on_stop()

        Thread(target=_async_stop).start()

    def should_stop(self):
        return self._stop


# vim:sw=4:ts=4:et:

