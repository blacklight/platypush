import importlib
import logging
import sys
import threading

from threading import Thread

from platypush.bus import Bus
from platypush.config import Config
from platypush.utils import get_message_class_by_type, set_timeout, clear_timeout
from platypush.message import Message
from platypush.message.event import Event, StopEvent
from platypush.message.request import Request
from platypush.message.response import Response

class Backend(Thread):
    """ Parent class for backends """

    _default_response_timeout = 5

    def __init__(self, bus=None, **kwargs):
        """
        Params:
            bus    -- Reference to the Platypush bus where the requests and the
                      responses will be posted [Bus]
            kwargs -- key-value configuration for this backend [Dict]
        """

        # If no bus is specified, create an internal queue where
        # the received messages will be pushed
        self.bus = bus or Bus()
        self.device_id = Config.get('device_id')
        self.thread_id = None
        self._stop = False
        self._kwargs = kwargs

        # Internal-only, we set the request context on a backend if that
        # backend is intended to react for a response to a specific request
        self._request_context = kwargs['_req_ctx'] if '_req_ctx' in kwargs \
            else None

        Thread.__init__(self)
        logging.basicConfig(stream=sys.stdout, level=Config.get('logging')
                            if 'logging' not in kwargs
                            else getattr(logging, kwargs['logging']))


    def on_message(self, msg):
        """
        Callback when a message is received on the backend.
        It parses and posts the message on the main bus.
        It should be called by the derived classes whenever
        a new message should be processed.

        Params:
            msg -- The message. It can be either a key-value
                   dictionary, a platypush.message.Message
                   object, or a string/byte UTF-8 encoded string
        """
        msg = Message.build(msg)

        if not getattr(msg, 'target') or msg.target != self.device_id:
            return  # Not for me

        logging.debug('Message received on the {} backend: {}'.format(
            self.__class__.__name__, msg))

        if self._is_expected_response(msg):
            # Expected response, trigger the response handler
            clear_timeout()
            self._request_context['on_response'](msg)
            self.stop()
            return

        if isinstance(msg, StopEvent) and msg.targets_me():
            logging.info('Received STOP event on {}'.format(self.__class__.__name__))
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
        Send an event message on the backend
        Params:
            event -- The request, either a dict, a string/bytes UTF-8 JSON,
                     or a platypush.message.event.Event object.
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
        Send a request message on the backend
        Params:
            request     -- The request, either a dict, a string/bytes UTF-8 JSON,
                           or a platypush.message.request.Request object.

            on_response -- Response handler, takes a platypush.message.response.Response
                           as argument. If set, the method will wait for a
                           response before exiting (default: None)
            response_timeout -- If on_response is set, the backend will raise
                                an exception if the response isn't received
                                within this number of seconds (default: 5)
        """

        request = Request.build(request)
        assert isinstance(request, Request)

        request.origin = self.device_id

        if on_response and response_timeout != 0:
            self._setup_response_handler(request, on_response, response_timeout)

        self.send_message(request, **kwargs)


    def send_response(self, response, request, **kwargs):
        """
        Send a response message on the backend
        Params:
            response -- The response, either a dict, a string/bytes UTF-8 JSON,
                        or a platypush.message.response.Response object
            request  -- Associated request, used to set the response parameters
                        that will link them
        """

        response = Response.build(response)
        assert isinstance(response, Response)
        assert isinstance(request, Request)

        response.id = request.id
        response.target = request.origin
        response.origin = self.device_id

        self.send_message(response, **kwargs)


    def send_message(self, msg, **kwargs):
        """
        Sends a platypush.message.Message to a node.
        To be implemented in the derived classes.
        Always call send_request or send_response instead of send_message directly

        Param:
            msg -- The message
        """

        raise NotImplementedError("send_message should be implemented in a derived class")


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

