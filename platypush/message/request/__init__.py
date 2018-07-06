import copy
import datetime
import json
import logging
import random
import re
import traceback

from threading import Thread

from platypush.config import Config
from platypush.context import get_plugin
from platypush.message import Message
from platypush.message.response import Response
from platypush.utils import get_hash, get_module_and_method_from_action

logger = logging.getLogger(__name__)


class Request(Message):
    """ Request message class """

    def __init__(self, target, action, origin=None, id=None, backend=None,
                 args=None, token=None):
        """
        Params:
            target -- Target node [String]
            action -- Action to be executed (e.g. music.mpd.play) [String]
            origin -- Origin node [String]
                id -- Message ID, or None to get it auto-generated
           backend -- Backend connected to the request, where the response will be delivered
              args -- Additional arguments for the action [Dict]
             token -- Authorization token, if required on the server [Str]
        """

        self.id      = id if id else self._generate_id()
        self.target  = target
        self.action  = action
        self.origin  = origin
        self.args    = args if args else {}
        self.backend = backend
        self.token   = token

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
        if 'token' in msg: args['token'] = msg['token']
        return cls(**args)

    @staticmethod
    def _generate_id():
        id = ''
        for i in range(0,16):
            id += '%.2x' % random.randint(0, 255)
        return id


    def _execute_procedure(self, *args, **kwargs):
        from platypush.config import Config
        from platypush.procedure import Procedure

        logger.info('Executing procedure request: {}'.format(self.action))
        proc_name = self.action.split('.')[-1]
        proc_config = Config.get_procedures()[proc_name]
        proc = Procedure.build(name=proc_name, requests=proc_config['actions'],
                               async=proc_config['async'],
                               backend=self.backend, id=self.id)

        return proc.execute(*args, **kwargs)


    def _expand_context(self, event_args=None, **context):
        from platypush.config import Config

        if event_args is None: event_args = copy.deepcopy(self.args)

        constants = Config.get_constants()
        context['constants'] = {}
        for (name,value) in constants.items():
            context['constants'][name] = value

        keys = []
        if isinstance(event_args, dict):
            keys = event_args.keys()
        elif isinstance(event_args, list):
            keys = range(0, len(event_args))

        for key in keys:
            value = event_args[key]

            if isinstance(value, str):
                value = self.expand_value_from_context(value, **context)
            elif isinstance(value, dict) or isinstance(value, list):
                self._expand_context(event_args=value, **context)

            event_args[key] = value

        return event_args


    @classmethod
    def expand_value_from_context(cls, value, **context):
        for (k, v) in context.items():
            if isinstance(v, Message):
                v = json.loads(str(v))
            try:
                exec('{}={}'.format(k, v))
            except:
                if isinstance(v, str):
                    try:
                        exec('{}="{}"'.format(k, re.sub('(^|[^\\\])"', '\1\\"', v)))
                    except:
                        pass

        parsed_value = ''
        while value:
            m = re.match('([^\$]*)(\${\s*(.+?)\s*})(.*)', value)
            if m and not m.group(1).endswith('\\'):
                prefix = m.group(1); expr = m.group(2);
                inner_expr = m.group(3); value = m.group(4)

                try:
                    context_value = eval(inner_expr)

                    if callable(context_value):
                        context_value = context_value()
                    if isinstance(context_value, datetime.date):
                        context_value = context_value.isoformat()
                except Exception as e:
                    logger.exception(e)
                    context_value = expr

                parsed_value += prefix + (
                    json.dumps(context_value)
                    if isinstance(context_value, list)
                    or isinstance(context_value, dict)
                    else str(context_value))
            else:
                parsed_value += value
                value = ''

        try: return json.loads(parsed_value)
        except ValueError as e: return parsed_value


    def _send_response(self, response):
        if self.backend and self.origin:
            self.backend.send_response(response=response, request=self)
        else:
            logger.info('Response whose request has no ' +
                        'origin attached: {}'.format(response))


    def execute(self, n_tries=1, async=True, **context):
        """
        Execute this request and returns a Response object
        Params:
            n_tries -- Number of tries in case of failure before raising a RuntimeError
            async   -- If True, the request will be run asynchronously and the
                       response posted on the bus when available (default),
                       otherwise the current thread will wait for the response
                       to be returned synchronously.
            context -- Key-valued context. Example:
                context = (group_name='Kitchen lights')
                request.args:
                    - group: ${group_name}  # will be expanded as "Kitchen lights")
        """

        def _thread_func(n_tries):
            if self.action.startswith('procedure.'):
                context['n_tries'] = n_tries
                response = self._execute_procedure(**context)
                self._send_response(response)
                return response
            else:
                (module_name, method_name) = get_module_and_method_from_action(self.action)
                plugin = get_plugin(module_name)

            try:
                # Run the action
                args = self._expand_context(**context)
                response = plugin.run(method=method_name, **args)

                if response and response.is_error():
                    raise RuntimeError('Response processed with errors: {}'.format(response))

                logger.info('Processed response from plugin {}: {}'.
                                format(plugin, str(response)))
            except Exception as e:
                # Retry mechanism
                response = Response(output=None, errors=[str(e), traceback.format_exc()])
                logger.exception(e)
                if n_tries:
                    logger.info('Reloading plugin {} and retrying'.format(module_name))
                    get_plugin(module_name, reload=True)
                    response = _thread_func(n_tries-1)
            finally:
                self._send_response(response)
                return response

        token_hash = Config.get('token_hash')

        if token_hash:
            if self.token is None or get_hash(self.token) != token_hash:
                raise PermissionError()

        if async:
            Thread(target=_thread_func, args=(n_tries,)).start()
        else:
            return _thread_func(n_tries)


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

