import errno
import hashlib
import importlib
import logging
import os
import signal

logger = logging.getLogger(__name__)

def get_module_and_method_from_action(action):
    """ Input  : action=music.mpd.play
        Output : ('music.mpd', 'play') """

    tokens = action.split('.')
    module_name = str.join('.', tokens[:-1])
    method_name = tokens[-1:][0]
    return (module_name, method_name)


def get_message_class_by_type(msgtype):
    """ Gets the class of a message type given as string """

    try:
        module = importlib.import_module('platypush.message.' + msgtype)
    except ImportError as e:
        logger.warning('Unsupported message type {}'.format(msgtype))
        raise RuntimeError(e)

    cls_name = msgtype[0].upper() + msgtype[1:]

    try:
        msgclass = getattr(module, cls_name)
    except AttributeError as e:
        logger.warning('No such class in {}: {}'.format(
            module.__name__, cls_name))
        raise RuntimeError(e)

    return msgclass


def get_event_class_by_type(type):
    """ Gets an event class by type name """
    event_module = importlib.import_module('.'.join(type.split('.')[:-1]))
    return getattr(event_module, type.split('.')[-1])


def set_timeout(seconds, on_timeout):
    """
    Set a function to be called if timeout expires without being cleared.
    It only works on the main thread.

    Params:
        seconds    -- Timeout in seconds
        on_timeout -- Function invoked on timeout unless clear_timeout is called before
    """

    def _sighandler(signum, frame):
        on_timeout()

    signal.signal(signal.SIGALRM, _sighandler)
    signal.alarm(seconds)


def clear_timeout():
    """ Clear any previously set timeout """
    signal.alarm(0)


def get_hash(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


# vim:sw=4:ts=4:et:

