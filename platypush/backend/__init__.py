import importlib
import logging
import sys
import threading

from threading import Thread

from platypush.bus import Bus
from platypush.config import Config
from platypush.utils import get_message_class_by_type
from platypush.message import Message
from platypush.message.event import Event, StopEvent
from platypush.message.request import Request
from platypush.message.response import Response

class Backend(Thread):
    """ Parent class for backends """

    def __init__(self, bus=None, **kwargs):
        """
        Params:
            bus    -- Reference to the Platypush bus where the requests and the
                      responses will be posted [Bus]
            kwargs -- key-value configuration for this backend [Dict]
        """

        # If no bus is specified, create an internal queue where
        # the received messages will be pushed
        self.bus = bus if bus else Bus()
        self.device_id = Config.get('device_id')
        self.thread_id = None
        self._stop = False

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

        msg = Message.parse(msg)
        if 'type' not in msg:
            logging.warning('Ignoring message with no type: {}'.format(msg))
            return

        msgtype = get_message_class_by_type(msg['type'])
        msg = msgtype.build(msg)

        if not getattr(msg, 'target') or msg.target != self.device_id:
            return  # Not for me

        logging.info('Message received on the {} backend: {}'.format(
            self.__class__.__name__, msg))

        msg.backend = self   # Augment message

        if isinstance(msg, StopEvent) and msg.targets_me():
            logging.info('Received STOP event on the {} backend: {}'.format(
                self.__class__.__name__, msg))
            self._stop = True
        else:
            self.bus.post(msg)

    def send_request(self, request):
        """
        Send a request message on the backend
        Params:
            request -- The request, either a dict, a string/bytes UTF-8 JSON,
                       or a platypush.message.request.Request object
        """

        request = Request.build(request)
        assert isinstance(request, Request)

        request.origin = self.device_id
        self.send_message(request)

    def send_response(self, response):
        """
        Send a response message on the backend
        Params:
            response -- The response, either a dict, a string/bytes UTF-8 JSON,
                        or a platypush.message.response.Response object
        """

        response = Response.build(response)
        assert isinstance(response, Response)

        response.origin = self.device_id
        self.send_message(response)


    def send_message(self, msg):
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
        evt = StopEvent(target=self.device_id, origin=self.device_id,
                        thread_id=self.thread_id)

        self.send_message(evt)
        self.on_stop()

    def should_stop(self):
        return self._stop


# vim:sw=4:ts=4:et:

