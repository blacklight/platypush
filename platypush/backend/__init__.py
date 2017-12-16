import json
import logging
import sys
import platypush

from threading import Thread

def _default_on_init(backend):
    logging.info('Backend {} initialized'.format(backend.__module__))


def _default_on_close(backend):
    logging.info('Backend {} terminated'.format(backend.__module__))


def _default_on_msg(backend, msg):
    logging.info('Received message: {}'.format(msg))


def _default_on_error(backend, error):
    logging.error(error)


class Backend(Thread):
    def __init__(self, config, mq = None,
                 on_init  = _default_on_init,
                 on_close = _default_on_close,
                 on_error = _default_on_error):
        self.config = config
        self.mq = mq
        self.on_init = on_init
        self.on_close = on_close
        self.on_error = on_error
        self.device_id = platypush.get_device_id()

        Thread.__init__(self)

        logging.basicConfig(stream=sys.stdout, level=platypush.get_logging_level()
                            if 'logging' not in config
                            else getattr(logging, config.pop('logging')))

        for cls in reversed(self.__class__.mro()):
            if cls is not object and hasattr(cls, '_init'):
                cls._init(self, **config)

    def is_local(self):
        from platypush.backend.local import LocalBackend
        return isinstance(self, LocalBackend)

    def on_msg(self, msg):
        if 'target' not in msg: return  # No target
        target = msg.pop('target')

        if target != self.device_id and not self.is_local():
            return  # Not for me

        if 'response' in msg:
            logging.info('Received response: {}'.format(msg))
            return

        if 'action' not in msg:
            self.on_error('No action specified: {}'.format(msg))
            return

        self.mq.put(msg)

    def send_msg(self, msg):
        if isinstance(msg, str):
            msg = json.loads(msg)
        if not isinstance(msg, dict):
            raise RuntimeError('send_msg expects either a JSON string or ' +
                               'a dictionary but received {}'.format(type(msg)))

        msg['origin'] = self.device_id  # To get the response

        self._send_msg(msg)

    def send_response(self, target, response):
        self.send_msg({
            'target'     : target,
            'response'   : {
                'output' : response.output,
                'errors' : response.errors,
            }
        })

    def run(self):
        raise NotImplementedError()

# vim:sw=4:ts=4:et:

