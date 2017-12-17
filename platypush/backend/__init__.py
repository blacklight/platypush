import importlib
import logging
import sys
import platypush

from queue import Queue
from threading import Thread

from platypush.message import Message
from platypush.message.request import Request
from platypush.message.response import Response

class Backend(Thread):
    """ Parent class for backends """

    def __init__(self, bus=None, **kwargs):
        """
        Params:
            bus    -- Reference to the Platypush bus where the requests and the
                      responses will be posted [Queue]
            kwargs -- key-value configuration for this backend [Dict]
        """

        # If no bus is specified, create an internal queue where
        # the received messages will be pushed
        self.bus = bus if bus else Queue()
        self.device_id = platypush.get_device_id()
        self.msgtypes = {}

        Thread.__init__(self)
        logging.basicConfig(stream=sys.stdout, level=platypush.get_logging_level()
                            if 'logging' not in kwargs
                            else getattr(logging, kwargs['logging']))

    def is_local(self):
        """ Returns true if this is a local backend """
        from platypush.backend.local import LocalBackend
        return isinstance(self, LocalBackend)

    def _get_msgtype_class(self, msgtype):
        """ Gets the class of a message type """

        if msgtype in self.msgtypes: return self.msgtypes[msgtype]

        try:
            module = importlib.import_module('platypush.message.' + msgtype)
        except ModuleNotFoundError as e:
            logging.warn('Unsupported message type {}'.format(msgtype))
            raise RuntimeError(e)

        cls_name = msgtype[0].upper() + msgtype[1:]

        try:
            msgclass = getattr(module, cls_name)
            self.msgtypes[msgtype] = msgclass
        except AttributeError as e:
            logging.warn('No such class in {}: {}'.format(
                module.__name__, cls_name))
            raise RuntimeError(e)

        return msgclass


    def on_msg(self, msg):
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
            logging.warn('Ignoring message with no type: {}'.format(msg))
            return

        msgtype = self._get_msgtype_class(msg['type'])
        msg = msgtype.build(msg)

        if not getattr(msg, 'target') or (msg.target != self.device_id and not self.is_local()):
            return  # Not for me

        logging.debug('Message received on the backend: {}'.format(msg))
        msg.backend = self   # Augment message
        self.bus.put(msg)

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
        self._send_msg(request)

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
        self._send_msg(response)

    def _send_msg(self, msg):
        """
        Sends a platypush.message.Message to a node.
        To be implemented in the derived classes.
        Always call send_request or send_response instead of _send_msg directly

        Param:
            msg -- The message
        """

        raise NotImplementedError("_send_msg should be implemented in a derived class")

    def run(self):
        """ Starts the backend thread. To be implemented in the derived classes """
        raise NotImplementedError("run should be implemented in a derived class")

# vim:sw=4:ts=4:et:

