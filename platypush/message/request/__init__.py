import json
import logging
import random
import traceback

from threading import Thread

from threading import Thread

from platypush.message import Message
from platypush.message.response import Response
from platypush.utils import get_or_load_plugin, get_module_and_name_from_action

class Request(Message):
    """ Request message class """

    def __init__(self, target, action, origin=None, id=None, args={}):
        """
        Params:
            target -- Target node [String]
            action -- Action to be executed (e.g. music.mpd.play) [String]
            origin -- Origin node [String]
                id -- Message ID, or None to get it auto-generated
              args -- Additional arguments for the action [Dict]
        """

        self.id      = id if id else self._generate_id()
        self.target  = target
        self.action  = action
        self.origin  = origin
        self.args    = args
        self.backend = None

    @classmethod
    def build(cls, msg):
        msg = super().parse(msg)
        args = {
            'target' : msg['target'],
            'action' : msg['action'],
            'args'   : msg['args'] if 'args' in msg else {},
        }

        args['id'] = msg['id'] if 'id' in msg else cls._generate_id()
        if 'origin' in msg: args['origin'] = msg['origin']
        return cls(**args)

    @staticmethod
    def _generate_id():
        id = ''
        for i in range(0,16):
            id += '%.2x' % random.randint(0, 255)
        return id

    def execute(self, n_tries=1):
        """
        Execute this request and returns a Response object
        Params:
            n_tries -- Number of tries in case of failure before raising a RuntimeError
        """
        def _thread_func(n_tries):
            (module_name, method_name) = get_module_and_name_from_action(self.action)

            plugin = get_or_load_plugin(module_name)

            try:
                # Run the action
                response = plugin.run(method=method_name, **self.args)
                if response and response.is_error():
                    raise RuntimeError('Response processed with errors: {}'.format(response))

                logging.info('Processed response from plugin {}: {}'.
                                format(plugin, response))
            except Exception as e:
                # Retry mechanism
                response = Response(output=None, errors=[str(e), traceback.format_exc()])
                logging.exception(e)
                if n_tries:
                    logging.info('Reloading plugin {} and retrying'.format(module_name))
                    get_or_load_plugin(module_name, reload=True)
                    _thread_func(n_tries-1)
                    return
            finally:
                # Send the response on the backend
                if self.backend and self.origin:
                    self.backend.send_response(response=response, request=self)
                else:
                    logging.info('Response whose request has no ' +
                                 'origin attached: {}'.format(response))

        Thread(target=_thread_func, args=(n_tries,)).start()


    def __str__(self):
        """
        Overrides the str() operator and converts
        the message into a UTF-8 JSON string
        """

        return json.dumps({
            'type'   : 'request',
            'target' : self.target,
            'action' : self.action,
            'args'   : self.args,
            'origin' : self.origin if hasattr(self, 'origin') else None,
            'id'     : self.id if hasattr(self, 'id') else None,
        })


# vim:sw=4:ts=4:et:

