import ast
import contextlib
import datetime
import hashlib
import importlib
import inspect
import logging
from multiprocessing import Lock as PLock
import os
import pathlib
import re
import signal
import socket
import ssl
import urllib.request
from threading import Lock as TLock
from typing import Generator, Optional, Tuple, Union

from dateutil import parser, tz
from redis import Redis
from rsa.key import PublicKey, PrivateKey, newkeys

logger = logging.getLogger('utils')
Lock = Union[PLock, TLock]  # type: ignore


def get_module_and_method_from_action(action):
    """
    Input: action=music.mpd.play
    Output: ('music.mpd', 'play')
    """

    tokens = action.split('.')
    module_name = str.join('.', tokens[:-1])
    method_name = tokens[-1:][0]
    return module_name, method_name


def get_message_class_by_type(msgtype):
    """Gets the class of a message type given as string"""

    try:
        module = importlib.import_module('platypush.message.' + msgtype)
    except ImportError as e:
        logger.warning('Unsupported message type %s', msgtype)
        raise RuntimeError(e) from e

    cls_name = msgtype[0].upper() + msgtype[1:]

    try:
        msgclass = getattr(module, cls_name)
    except AttributeError as e:
        logger.warning('No such class in %s: %s', module.__name__, cls_name)
        raise RuntimeError(e) from e

    return msgclass


def get_event_class_by_type(type):  # pylint: disable=redefined-builtin
    """Gets an event class by type name"""
    event_module = importlib.import_module('.'.join(type.split('.')[:-1]))
    return getattr(event_module, type.split('.')[-1])


def get_plugin_module_by_name(plugin_name):
    """Gets the module of a plugin by name (e.g. "music.mpd" or "media.vlc")"""

    module_name = 'platypush.plugins.' + plugin_name
    try:
        return importlib.import_module('platypush.plugins.' + plugin_name)
    except ImportError as e:
        logger.error('Cannot import %s: %s', module_name, e)
        return None


def get_backend_module_by_name(backend_name):
    """Gets the module of a backend by name (e.g. "backend.http" or "backend.mqtt")"""

    module_name = 'platypush.backend.' + backend_name
    try:
        return importlib.import_module('platypush.backend.' + backend_name)
    except ImportError as e:
        logger.error('Cannot import %s: %s', module_name, e)
        return None


def get_plugin_class_by_name(plugin_name):
    """Gets the class of a plugin by name (e.g. "music.mpd" or "media.vlc")"""

    module = get_plugin_module_by_name(plugin_name)
    if not module:
        return

    class_name = getattr(
        module, ''.join([_.capitalize() for _ in plugin_name.split('.')]) + 'Plugin'
    )
    try:
        return getattr(
            module, ''.join([_.capitalize() for _ in plugin_name.split('.')]) + 'Plugin'
        )
    except Exception as e:
        logger.error('Cannot import class %s: %s', class_name, e)
        return None


def get_plugin_name_by_class(plugin) -> Optional[str]:
    """Gets the common name of a plugin (e.g. "music.mpd" or "media.vlc") given its class."""

    from platypush.plugins import Plugin

    if isinstance(plugin, Plugin):
        plugin = plugin.__class__

    class_name = plugin.__name__
    class_tokens = [
        token.lower()
        for token in re.sub(r'([A-Z])', r' \1', class_name).split(' ')
        if token.strip() and token != 'Plugin'
    ]

    return '.'.join(class_tokens)


def get_backend_class_by_name(backend_name: str):
    """Gets the class of a backend by name (e.g. "backend.http" or "backend.mqtt")"""

    module = get_backend_module_by_name(backend_name)
    if not module:
        return

    class_name = getattr(
        module,
        ''.join(
            [
                token.capitalize()
                for i, token in enumerate(backend_name.split('.'))
                if not (i == 0 and token == 'backend')
            ]
        )
        + 'Backend',
    )
    try:
        return getattr(
            module,
            ''.join([_.capitalize() for _ in backend_name.split('.')]) + 'Backend',
        )
    except Exception as e:
        logger.error('Cannot import class %s: %s', class_name, e)
        return None


def get_backend_name_by_class(backend) -> Optional[str]:
    """Gets the common name of a backend (e.g. "http" or "mqtt") given its class."""

    from platypush.backend import Backend

    if isinstance(backend, Backend):
        backend = backend.__class__

    class_name = backend.__name__
    class_tokens = [
        token.lower()
        for token in re.sub(r'([A-Z])', r' \1', class_name).split(' ')
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

    def _sighandler(*_):
        on_timeout()

    signal.signal(signal.SIGALRM, _sighandler)
    signal.alarm(seconds)


def clear_timeout():
    """Clear any previously set timeout"""
    signal.alarm(0)


def get_hash(s):
    """Get the SHA256 hash hex digest of a string input"""
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def get_decorators(cls, climb_class_hierarchy=False):
    """
    Get the decorators of a class as a {"decorator_name": [list of methods]} dictionary

    :param cls: Class type
    :param climb_class_hierarchy: If set to True (default: False), it will search return the decorators in the parent
        classes as well
    :type climb_class_hierarchy: bool
    """

    decorators = {}

    # noinspection PyPep8Naming
    def visit_FunctionDef(node):
        for n in node.decorator_list:
            if isinstance(n, ast.Call):
                # noinspection PyUnresolvedReferences
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
        with contextlib.suppress(TypeError):
            node_iter.visit(ast.parse(inspect.getsource(target)))

    return decorators


def get_redis_queue_name_by_message(msg) -> Optional[str]:
    """
    Get the Redis queue name for the response(s) associated to a request
    message.

    :param msg: Input message, as a :class:`platypush.message.request.Request`
        object.
    """
    from platypush.message.request import Request

    if not isinstance(msg, Request):
        logger.warning('Not a valid request (type: %s): %s', type(msg), msg)
        return None
    return f'platypush/responses/{msg.id}' if msg.id else None


def _get_ssl_context(
    context_type=None, ssl_cert=None, ssl_key=None, ssl_cafile=None, ssl_capath=None
):
    if not context_type:
        ssl_context = ssl.create_default_context(cafile=ssl_cafile, capath=ssl_capath)
    else:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    if ssl_cafile or ssl_capath:
        ssl_context.load_verify_locations(cafile=ssl_cafile, capath=ssl_capath)

    ssl_context.load_cert_chain(
        certfile=os.path.abspath(os.path.expanduser(ssl_cert)),
        keyfile=os.path.abspath(os.path.expanduser(ssl_key)) if ssl_key else None,
    )

    return ssl_context


def get_ssl_context(ssl_cert=None, ssl_key=None, ssl_cafile=None, ssl_capath=None):
    """
    Generic builder for SSL context.
    """
    return _get_ssl_context(
        context_type=None,
        ssl_cert=ssl_cert,
        ssl_key=ssl_key,
        ssl_cafile=ssl_cafile,
        ssl_capath=ssl_capath,
    )


def get_ssl_server_context(
    ssl_cert=None, ssl_key=None, ssl_cafile=None, ssl_capath=None
):
    """
    Builder for a server-side SSL context.
    """
    return _get_ssl_context(
        context_type=ssl.PROTOCOL_TLS_SERVER,
        ssl_cert=ssl_cert,
        ssl_key=ssl_key,
        ssl_cafile=ssl_cafile,
        ssl_capath=ssl_capath,
    )


def get_ssl_client_context(
    ssl_cert=None, ssl_key=None, ssl_cafile=None, ssl_capath=None
):
    """
    Builder for a client-side SSL context.
    """
    return _get_ssl_context(
        context_type=ssl.PROTOCOL_TLS_CLIENT,
        ssl_cert=ssl_cert,
        ssl_key=ssl_key,
        ssl_cafile=ssl_cafile,
        ssl_capath=ssl_capath,
    )


def set_thread_name(name: str):
    """
    Set the name of the current thread.
    """
    try:
        import prctl

        prctl.set_name(name)  # pylint: disable=no-member
    except ImportError:
        logger.debug('Unable to set thread name: prctl module is missing')


def find_bins_in_path(bin_name):
    """
    Search for a binary in the PATH variable.
    """
    return [
        os.path.join(p, bin_name)
        for p in os.environ.get('PATH', '').split(':')
        if os.path.isfile(os.path.join(p, bin_name))
        and (os.name == 'nt' or os.access(os.path.join(p, bin_name), os.X_OK))
    ]


def find_files_by_ext(directory, *exts):
    """
    Finds all the files in the given directory with the provided extensions.
    """

    if not exts:
        raise AttributeError('No extensions provided')

    if not os.path.isdir(directory):
        raise AttributeError(f'{directory} is not a valid directory')

    min_len = len(min(exts, key=len))
    max_len = len(max(exts, key=len))
    result = []

    for _, __, files in os.walk(directory):
        for i in range(min_len, max_len + 1):
            result += [f for f in files if f[-i:] in exts]

    return result


def is_process_alive(pid: int) -> bool:
    """
    :param pid: Process ID.
    :return: True if the process with the given PID is alive.
    """
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_ip_or_hostname() -> str:
    """
    Get the the default IP address or hostname of the machine.
    """
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith('127.') or ip.startswith('::1'):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(('10.255.255.255', 1))
            ip = sock.getsockname()[0]
            sock.close()
        except Exception as e:
            logger.debug(e)

    return ip


def get_mime_type(resource: str) -> Optional[str]:
    """
    Get the MIME type of the given resource.

    :param resource: The resource to get the MIME type for - it can be a file
        path or a URL.
    """
    import magic

    if resource.startswith('file://'):
        offset = len('file://')
        resource = resource[offset:]

    # noinspection HttpUrlsUsage
    if resource.startswith('http://') or resource.startswith('https://'):
        with urllib.request.urlopen(resource) as response:
            return response.info().get_content_type()
    else:
        if hasattr(magic, 'detect_from_filename'):
            mime = magic.detect_from_filename(resource)  # type: ignore
        elif hasattr(magic, 'from_file'):
            mime = magic.from_file(resource, mime=True)
        else:
            raise RuntimeError(
                'The installed magic version provides neither detect_from_filename nor from_file'
            )

        if mime:
            return mime.mime_type if hasattr(mime, 'mime_type') else mime  # type: ignore

    return None


def camel_case_to_snake_case(string):
    """
    Utility function to convert CamelCase to snake_case.
    """
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
        return zip_longest(*args, fillvalue=fillvalue)

    for chunk in zip_longest(*args):
        yield filter(None, chunk)


def is_functional_procedure(obj) -> bool:
    """
    Check if the given object is a functional procedure.
    """
    return callable(obj) and hasattr(obj, 'procedure')


def is_functional_hook(obj) -> bool:
    """
    Check if the given object is a functional hook.
    """
    return callable(obj) and hasattr(obj, 'hook')


def is_functional_cron(obj) -> bool:
    """
    Check if the given object is a functional cron.
    """
    return callable(obj) and hasattr(obj, 'cron') and hasattr(obj, 'cron_expression')


def run(action, *args, **kwargs):
    """
    Run the given action with the given arguments. Example:

        >>> from platypush.utils import run
        >>> run('music.mpd.play', resource='file:///home/user/music.mp3')

    """
    from platypush.context import get_plugin

    (module_name, method_name) = get_module_and_method_from_action(action)
    plugin = get_plugin(module_name)
    method = getattr(plugin, method_name)
    response = method(*args, **kwargs)

    if response.errors:
        raise RuntimeError(response.errors[0])

    return response.output


def generate_rsa_key_pair(
    key_file: Optional[str] = None, size: int = 2048
) -> Tuple[PublicKey, PrivateKey]:
    """
    Generate an RSA key pair.

    :param key_file: Target file for the private key (the associated public key will be stored in ``<key_file>.pub``.
        If no key file is specified then the public and private keys will be returned in ASCII format in a dictionary
        with the following structure:

            .. code-block:: json

                {
                    "private": "private key here",
                    "public": "public key here"
                }

    :param size: Key size (default: 2048 bits).
    :return: A tuple with the generated ``(priv_key_str, pub_key_str)``.
    """
    logger.info('Generating RSA keypair')
    pub_key, priv_key = newkeys(size)
    logger.info('Generated RSA keypair')
    public_key_str = pub_key.save_pkcs1('PEM').decode()
    private_key_str = priv_key.save_pkcs1('PEM').decode()

    if key_file:
        logger.info('Saving private key to %s', key_file)
        with open(os.path.expanduser(key_file), 'w') as f1, open(
            os.path.expanduser(key_file) + '.pub', 'w'
        ) as f2:
            f1.write(private_key_str)
            f2.write(public_key_str)
            os.chmod(key_file, 0o600)

    return pub_key, priv_key


def get_or_generate_jwt_rsa_key_pair():
    """
    Get or generate a JWT RSA key pair.
    """
    from platypush.config import Config

    key_dir = os.path.join(Config.get('workdir'), 'jwt')
    priv_key_file = os.path.join(key_dir, 'id_rsa')
    pub_key_file = priv_key_file + '.pub'

    if os.path.isfile(priv_key_file) and os.path.isfile(pub_key_file):
        with open(pub_key_file, 'r') as f1, open(priv_key_file, 'r') as f2:
            return (
                PublicKey.load_pkcs1(f1.read().encode()),
                PrivateKey.load_pkcs1(f2.read().encode()),
            )

    pathlib.Path(key_dir).mkdir(parents=True, exist_ok=True, mode=0o755)
    return generate_rsa_key_pair(priv_key_file, size=2048)


def get_enabled_plugins() -> dict:
    """
    Get the enabled plugins.

    :return: A dictionary with the enabled plugins, in the format ``name`` ->
        :class:`platypush.plugins.Plugin` instance.
    """
    from platypush.config import Config
    from platypush.context import get_plugin

    plugins = {}
    for name in Config.get_plugins():
        try:
            plugin = get_plugin(name)
            if plugin:
                plugins[name] = plugin
        except Exception as e:
            logger.warning('Could not initialize plugin %s', name)
            logger.exception(e)

    return plugins


def get_redis(*args, **kwargs) -> Redis:
    """
    Get a Redis client on the basis of the Redis configuration.

    The Redis configuration can be loaded from:

        1. The ``backend.redis`` configuration (``redis_args`` attribute)
        2. The ``redis`` plugin.

    """
    from platypush.config import Config

    if not (args or kwargs):
        kwargs = (
            (Config.get('backend.redis') or {}).get('redis_args', {})
            or Config.get('redis')
            or {}
        )

    return Redis(*args, **kwargs)


def to_datetime(t: Union[str, int, float, datetime.datetime]) -> datetime.datetime:
    """
    Utility function to convert a datetime/timestamp provided as a
    string/integer/float/datetime to a ``datetime.datetime`` instance.
    """
    if isinstance(t, (int, float)):
        return datetime.datetime.fromtimestamp(t, tz=tz.tzutc())
    if isinstance(t, str):
        return parser.parse(t)
    return t


@contextlib.contextmanager
def get_lock(
    lock: Lock, timeout: Optional[float] = None
) -> Generator[bool, None, None]:
    """
    Get a lock with an optional timeout through a context manager construct:

        >>> from threading import Lock
        >>> lock = Lock()
        >>> with get_lock(lock, timeout=2):
        >>>     ...

    """
    kwargs = {'timeout': timeout} if timeout else {}
    result = lock.acquire(**kwargs)

    try:
        if not result:
            raise TimeoutError()
        yield result
    finally:
        if result:
            lock.release()


# vim:sw=4:ts=4:et:
