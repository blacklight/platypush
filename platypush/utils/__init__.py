import ast
import hashlib
import importlib
import inspect
import logging
import os
import re
import signal
import socket
import ssl
import urllib.request
from typing import Optional

logger = logging.getLogger('utils')


def get_module_and_method_from_action(action):
    """ Input  : action=music.mpd.play
        Output : ('music.mpd', 'play') """

    tokens = action.split('.')
    module_name = str.join('.', tokens[:-1])
    method_name = tokens[-1:][0]
    return module_name, method_name


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


def get_plugin_module_by_name(plugin_name):
    """ Gets the module of a plugin by name (e.g. "music.mpd" or "media.vlc") """

    module_name = 'platypush.plugins.' + plugin_name
    try:
        return importlib.import_module('platypush.plugins.' + plugin_name)
    except ImportError as e:
        logger.error('Cannot import {}: {}'.format(module_name, str(e)))
        return None


def get_plugin_class_by_name(plugin_name):
    """ Gets the class of a plugin by name (e.g. "music.mpd" or "media.vlc") """

    module = get_plugin_module_by_name(plugin_name)
    if not module:
        return

    class_name = getattr(module, ''.join([_.capitalize() for _ in plugin_name.split('.')]) + 'Plugin')
    try:
        return getattr(module, ''.join([_.capitalize() for _ in plugin_name.split('.')]) + 'Plugin')
    except Exception as e:
        logger.error('Cannot import class {}: {}'.format(class_name, str(e)))
        return None


def get_plugin_name_by_class(plugin) -> Optional[str]:
    """Gets the common name of a plugin (e.g. "music.mpd" or "media.vlc") given its class. """

    from platypush.plugins import Plugin

    if isinstance(plugin, Plugin):
        plugin = plugin.__class__

    class_name = plugin.__name__
    class_tokens = [
        token.lower() for token in re.sub(r'([A-Z])', r' \1', class_name).split(' ')
        if token.strip() and token != 'Plugin'
    ]

    return '.'.join(class_tokens)


def get_backend_name_by_class(backend) -> Optional[str]:
    """Gets the common name of a backend (e.g. "http" or "mqtt") given its class. """

    from platypush.backend import Backend

    if isinstance(backend, Backend):
        backend = backend.__class__

    class_name = backend.__name__
    class_tokens = [
        token.lower() for token in re.sub(r'([A-Z])', r' \1', class_name).split(' ')
        if token.strip() and token != 'Backend'
    ]

    return '.'.join(class_tokens)


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
    """ Get the SHA256 hash hexdigest of a string input """
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def get_decorators(cls, climb_class_hierarchy=False):
    """
    Get the decorators of a class as a {"decorator_name": [list of methods]} dictionary
    :param climb_class_hierarchy: If set to True (default: False), it will search return the decorators in the parent classes as well
    :type climb_class_hierarchy: bool
    """

    decorators = {}

    def visit_FunctionDef(node):
        for n in node.decorator_list:
            if isinstance(n, ast.Call):
                name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
            else:
                name = n.attr if isinstance(n, ast.Attribute) else n.id

            decorators[name] = decorators.get(name, set())
            decorators[name].add(node.name)

    if climb_class_hierarchy:
        targets = inspect.getmro(cls)
    else:
        targets = [cls]

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = visit_FunctionDef

    for target in targets:
        try:
            node_iter.visit(ast.parse(inspect.getsource(target)))
        except TypeError:
            # Ignore built-in classes
            pass

    return decorators


def get_redis_queue_name_by_message(msg):
    from platypush.message import Message

    if not isinstance(msg, Message):
        logger.warning('Not a valid message (type: {}): {}'.format(type(msg), msg))

    return 'platypush/responses/{}'.format(msg.id) if msg.id else None


def _get_ssl_context(context_type=None, ssl_cert=None, ssl_key=None,
                     ssl_cafile=None, ssl_capath=None):
    if not context_type:
        ssl_context = ssl.create_default_context(cafile=ssl_cafile,
                                                 capath=ssl_capath)
    else:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    if ssl_cafile or ssl_capath:
        ssl_context.load_verify_locations(
            cafile=ssl_cafile, capath=ssl_capath)

    ssl_context.load_cert_chain(
        certfile=os.path.abspath(os.path.expanduser(ssl_cert)),
        keyfile=os.path.abspath(os.path.expanduser(ssl_key)) if ssl_key else None
    )

    return ssl_context


def get_ssl_context(ssl_cert=None, ssl_key=None, ssl_cafile=None,
                    ssl_capath=None):
    return _get_ssl_context(context_type=None,
                            ssl_cert=ssl_cert, ssl_key=ssl_key,
                            ssl_cafile=ssl_cafile, ssl_capath=ssl_capath)


def get_ssl_server_context(ssl_cert=None, ssl_key=None, ssl_cafile=None,
                           ssl_capath=None):
    return _get_ssl_context(context_type=ssl.PROTOCOL_TLS_SERVER,
                            ssl_cert=ssl_cert, ssl_key=ssl_key,
                            ssl_cafile=ssl_cafile, ssl_capath=ssl_capath)


def get_ssl_client_context(ssl_cert=None, ssl_key=None, ssl_cafile=None,
                           ssl_capath=None):
    return _get_ssl_context(context_type=ssl.PROTOCOL_TLS_CLIENT,
                            ssl_cert=ssl_cert, ssl_key=ssl_key,
                            ssl_cafile=ssl_cafile, ssl_capath=ssl_capath)

def set_thread_name(name):
    global logger

    try:
        import prctl
        prctl.set_name(name)
    except ImportError:
        logger.debug('Unable to set thread name: prctl module is missing')


def find_bins_in_path(bin_name):
    return [os.path.join(p, bin_name)
            for p in os.environ.get('PATH', '').split(':')
            if os.path.isfile(os.path.join(p, bin_name))
            and (os.name == 'nt' or
                 os.access(os.path.join(p, bin_name), os.X_OK))]


def find_files_by_ext(directory, *exts):
    """
    Finds all the files in the given directory with the provided extensions
    """

    if not exts:
        raise AttributeError('No extensions provided')

    if not os.path.isdir(directory):
        raise AttributeError('{} is not a valid directory'.format(directory))

    min_len = len(min(exts, key=len))
    max_len = len(max(exts, key=len))
    result = []

    for root, dirs, files in os.walk(directory):
        for i in range(min_len, max_len+1):
            result += [f for f in files if f[-i:] in exts]

    return result


def is_process_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_ip_or_hostname():
    ip = socket.gethostbyname(socket.gethostname())
    return socket.getfqdn() if ip.startswith('127.') else ip


def get_mime_type(resource):
    import magic
    if resource.startswith('file://'):
        resource = resource[len('file://'):]

    if resource.startswith('http://') or resource.startswith('https://'):
        with urllib.request.urlopen(resource) as response:
            return response.info().get_content_type()
    else:
        if hasattr(magic, 'detect_from_filename'):
            mime = magic.detect_from_filename(resource)
        elif hasattr(magic, 'from_file'):
            mime = magic.from_file(resource, mime=True)
        else:
            raise RuntimeError('The installed magic version provides neither detect_from_filename nor from_file')

        if mime:
            return mime.mime_type


def camel_case_to_snake_case(string):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def grouper(n, iterable, fillvalue=None):
    """
    Split an iterable in groups of max N elements.
    grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    """
    from itertools import zip_longest
    args = [iter(iterable)] * n

    if fillvalue:
        return zip_longest(fillvalue=fillvalue, *args)

    for chunk in zip_longest(*args):
        yield filter(None, chunk)


def is_functional_procedure(obj) -> bool:
    return callable(obj) and hasattr(obj, 'procedure')


def is_functional_hook(obj) -> bool:
    return callable(obj) and hasattr(obj, 'hook')


def is_functional_cron(obj) -> bool:
    return callable(obj) and hasattr(obj, 'cron') and hasattr(obj, 'cron_expression')


def run(action, *args, **kwargs):
    from platypush.context import get_plugin
    (module_name, method_name) = get_module_and_method_from_action(action)
    plugin = get_plugin(module_name)
    method = getattr(plugin, method_name)
    response = method(*args, **kwargs)

    if response.errors:
        raise RuntimeError(response.errors[0])

    return response.output


# vim:sw=4:ts=4:et:
