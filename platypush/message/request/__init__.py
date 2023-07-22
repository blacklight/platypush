import copy
import datetime
import json
import logging
import random
import re
import time

from threading import Thread

from platypush.config import Config
from platypush.context import get_plugin
from platypush.message import Message
from platypush.message.response import Response
from platypush.utils import (
    get_hash,
    get_module_and_method_from_action,
    get_redis_queue_name_by_message,
    is_functional_procedure,
)

logger = logging.getLogger('platypush')


class Request(Message):
    """Request message class"""

    def __init__(
        self,
        target,
        action,
        origin=None,
        id=None,
        backend=None,
        args=None,
        token=None,
        timestamp=None,
    ):
        """
        Params:
            target -- Target node [Str]
            action -- Action to be executed (e.g. music.mpd.play) [Str]
            origin -- Origin node [Str]
                id -- Message ID, or None to get it auto-generated
           backend -- Backend connected to the request, where the response will be delivered
              args -- Additional arguments for the action [Dict]
             token -- Authorization token, if required on the server [Str]
         timestamp -- Message creation timestamp [Float]
        """

        super().__init__(timestamp=timestamp)

        self.id = id if id else self._generate_id()
        self.target = target
        self.action = action
        self.origin = origin
        self.args = args if args else {}
        self.backend = backend
        self.token = token
        self._logger = logging.getLogger('platypush:requests')

    @classmethod
    def build(cls, msg):
        msg = super().parse(msg)
        args = {
            'target': msg.get('target', Config.get('device_id')),
            'action': msg['action'],
            'args': msg.get('args', {}),
            'id': msg['id'] if 'id' in msg else cls._generate_id(),
            'timestamp': msg['_timestamp'] if '_timestamp' in msg else time.time(),
        }

        if 'origin' in msg:
            args['origin'] = msg['origin']
        if 'token' in msg:
            args['token'] = msg['token']
        return cls(**args)

    @staticmethod
    def _generate_id():
        return ''.join(f'{random.randint(0, 255):02x}' for _ in range(0, 16))

    def _execute_procedure(self, *args, **kwargs):
        from platypush.procedure import Procedure

        procedures = Config.get_procedures()
        proc_name = '.'.join(self.action.split('.')[1:])
        if proc_name not in procedures:
            proc_name = self.action.split('.')[-1]

        proc_config = procedures[proc_name]
        if is_functional_procedure(proc_config):
            self._expand_context(self.args, **kwargs)
            kwargs = {**self.args, **kwargs}
            if 'n_tries' in kwargs:
                del kwargs['n_tries']

            return proc_config(*args, **kwargs)

        proc = Procedure.build(
            name=proc_name,
            requests=proc_config['actions'],
            _async=proc_config['_async'],
            args=self.args,
            backend=self.backend,
            id=self.id,
        )

        return proc.execute(*args, **kwargs)

    def _expand_context(self, event_args=None, **context):
        from platypush.config import Config

        if event_args is None:
            event_args = copy.deepcopy(self.args)

        constants = Config.get_constants()
        context['constants'] = {}
        for name, value in constants.items():
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
            elif isinstance(value, (dict, list)):
                self._expand_context(event_args=value, **context)

            event_args[key] = value

        return event_args

    @classmethod
    def expand_value_from_context(cls, _value, **context):
        for k, v in context.items():
            if isinstance(v, Message):
                v = json.loads(str(v))
            try:
                exec('{}={}'.format(k, v))
            except Exception:
                if isinstance(v, str):
                    try:
                        exec('{}="{}"'.format(k, re.sub(r'(^|[^\\])"', '\1\\"', v)))
                    except Exception as e2:
                        logger.debug(
                            'Could not set context variable %s=%s: %s', k, v, e2
                        )
                        logger.debug('Context: %s', context)

        parsed_value = ''
        if not isinstance(_value, str):
            parsed_value = _value

        while _value and isinstance(_value, str):
            m = re.match(r'([^$]*)(\${\s*(.+?)\s*})(.*)', _value)
            if m and not m.group(1).endswith('\\'):
                prefix = m.group(1)
                expr = m.group(2)
                inner_expr = m.group(3)
                _value = m.group(4)

                try:
                    context_value = eval(inner_expr)

                    if callable(context_value):
                        context_value = context_value()
                    if isinstance(context_value, (range, tuple)):
                        context_value = [*context_value]
                    if isinstance(context_value, datetime.date):
                        context_value = context_value.isoformat()
                except Exception as e:
                    logger.exception(e)
                    context_value = expr

                parsed_value += prefix + (
                    json.dumps(context_value)
                    if isinstance(context_value, (list, dict))
                    else str(context_value)
                )
            else:
                parsed_value += _value
                _value = ''

        try:
            return json.loads(parsed_value)
        except (ValueError, TypeError):
            return parsed_value

    def _send_response(self, response):
        response = Response.build(response)
        response.id = self.id
        response.target = self.origin
        response.origin = Config.get('device_id')
        response.log()

        if self.backend and self.origin:
            self.backend.send_response(response=response, request=self)
        else:
            redis = get_plugin('redis')
            if redis:
                queue_name = get_redis_queue_name_by_message(self)
                redis.send_message(queue_name, response)
                redis.expire(queue_name, 60)

    def execute(self, n_tries=1, _async=True, **context):
        """
        Execute this request and returns a Response object
        Params:
            n_tries -- Number of tries in case of failure before raising a RuntimeError
            _async   -- If True, the request will be run asynchronously and the
                       response posted on the bus when available (default),
                       otherwise the current thread will wait for the response
                       to be returned synchronously.
            context -- Key-valued context. Example:
                context = (group_name='Kitchen lights')
                request.args:
                    - group: ${group_name}  # will be expanded as "Kitchen lights")
        """

        def _thread_func(_n_tries, errors=None):
            from platypush.context import get_bus
            from platypush.plugins import RunnablePlugin

            response = None
            self.log()

            try:
                if self.action.startswith('procedure.'):
                    context['n_tries'] = _n_tries
                    response = self._execute_procedure(**context)
                    if response is not None:
                        self._send_response(response)
                    return response

                # utils.get_context is a special action that simply returns the current context
                if self.action == 'utils.get_context':
                    response = Response(output=context)
                    self._send_response(response)
                    return response

                action = self.expand_value_from_context(self.action, **context)
                (module_name, method_name) = get_module_and_method_from_action(action)
                plugin = get_plugin(module_name)
                assert plugin, f'No such plugin: {module_name}'
            except Exception as e:
                logger.exception(e)
                response = Response(output=None, errors=[str(e)])
                self._send_response(response)
                return response

            try:
                # Run the action
                args = self._expand_context(**context)
                args = self.expand_value_from_context(args, **context)
                if isinstance(args, dict):
                    response = plugin.run(method_name, **args)
                elif isinstance(args, list):
                    response = plugin.run(method_name, *args)
                else:
                    response = plugin.run(method_name, args)

                if response is None:
                    response = Response()
            except (AssertionError, TimeoutError) as e:
                error = e if str(e) else e.__class__.__name__
                logger.warning(
                    '%s from action [%s]: %s',
                    e.__class__.__name__,
                    action,
                    error,
                )
                response = Response(output=None, errors=[error])
            except Exception as e:
                # Retry mechanism
                plugin.logger.exception(e)
                errors = errors or []
                if str(e) not in errors:
                    errors.append(str(e))

                response = Response(output=None, errors=errors)
                if _n_tries - 1 > 0:
                    logger.info('Reloading plugin %s and retrying', module_name)
                    plugin = get_plugin(module_name, reload=True)
                    if isinstance(plugin, RunnablePlugin):
                        plugin.bus = get_bus()
                        plugin.start()

                    response = _thread_func(_n_tries=_n_tries - 1, errors=errors)
            finally:
                self._send_response(response)

            return response

        stored_token_hash = Config.get('token_hash')
        token = getattr(self, 'token', '')
        if stored_token_hash and get_hash(token) != stored_token_hash:
            raise PermissionError()

        if _async:
            Thread(target=_thread_func, args=(n_tries,)).start()
        else:
            return _thread_func(n_tries)

    def __str__(self):
        """
        Overrides the str() operator and converts
        the message into a UTF-8 JSON string
        """

        return json.dumps(
            {
                'type': 'request',
                'target': self.target,
                'action': self.action,
                'args': self.args,
                'origin': self.origin if hasattr(self, 'origin') else None,
                'id': self.id if hasattr(self, 'id') else None,
                'token': self.token if hasattr(self, 'token') else None,
                '_timestamp': self.timestamp,
            }
        )


# vim:sw=4:ts=4:et:
