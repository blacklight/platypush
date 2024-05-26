import enum
import logging
import re
from functools import wraps

from queue import LifoQueue
from typing import Optional

from ..common import exec_wrapper
from ..config import Config
from ..message.request import Request
from ..message.response import Response

logger = logging.getLogger('platypush')


class Statement(enum.Enum):
    """
    Enumerates the possible statements in a procedure.
    """

    BREAK = 'break'
    CONTINUE = 'continue'
    RETURN = 'return'


class Procedure:
    """Procedure class. A procedure is a pre-configured list of requests"""

    def __init__(self, name, _async, requests, args=None, backend=None):
        """
        Params:
            name     -- Procedure name
            _async   -- Whether the actions in the procedure are supposed to
                        be executed sequentially or in parallel (True or False)
            requests -- List of platypush.message.request.Request objects
        """

        self.name = name
        self._async = _async
        self.requests = requests
        self.backend = backend
        self.args = args or {}
        self._should_return = False

        for req in requests:
            req.backend = self.backend

    @classmethod
    # pylint: disable=too-many-branches,too-many-statements
    def build(
        cls,
        name,
        _async,
        requests,
        args=None,
        backend=None,
        id=None,  # pylint: disable=redefined-builtin
        procedure_class=None,
        **kwargs,
    ):
        reqs = []
        for_count = 0
        while_count = 0
        if_count = 0
        if_config = LifoQueue()
        procedure_class = procedure_class or cls
        key = None

        for request_config in requests:
            # Check if it's a break/continue/return statement
            if isinstance(request_config, str):
                reqs.append(Statement(request_config))
                continue

            # Check if this request is an if-else
            if len(request_config.keys()) >= 1:
                key = list(request_config.keys())[0]
                m = re.match(r'\s*(if)\s+\${(.*)}\s*', key)

                if m:
                    if_count += 1
                    if_name = f'{name}__if_{if_count}'
                    condition = m.group(2)

                    if_config.put(
                        {
                            'name': if_name,
                            '_async': False,
                            'requests': request_config[key],
                            'condition': condition,
                            'else_branch': [],
                            'backend': backend,
                            'id': id,
                        }
                    )

                    continue

                if key == 'else':
                    if if_config.empty():
                        raise RuntimeError(
                            f'else statement with no associated if in {name}'
                        )

                    conf = if_config.get()
                    conf['else_branch'] = request_config[key]
                    if_config.put(conf)

            if not if_config.empty():
                reqs.append(IfProcedure.build(**(if_config.get())))
                if key == 'else':
                    continue

            # Check if this request is a for loop
            if len(request_config.keys()) == 1:
                key = list(request_config.keys())[0]
                m = re.match(r'\s*(fork?)\s+([\w\d_]+)\s+in\s+(.*)\s*', key)

                if m:
                    for_count += 1
                    loop_name = f'{name}__for_{for_count}'

                    # A 'for' loop is synchronous. Declare a 'fork' loop if you
                    # want to process the elements in the iterable in parallel
                    _async = m.group(1) == 'fork'
                    iterator_name = m.group(2)
                    iterable = m.group(3)

                    loop = ForProcedure.build(
                        name=loop_name,
                        _async=_async,
                        requests=request_config[key],
                        backend=backend,
                        id=id,
                        iterator_name=iterator_name,
                        iterable=iterable,
                    )

                    reqs.append(loop)
                    continue

            # Check if this request is a while loop
            if len(request_config.keys()) == 1:
                key = list(request_config.keys())[0]
                m = re.match(r'\s*while\s+\${(.*)}\s*', key)

                if m:
                    while_count += 1
                    loop_name = f'{name}__while_{while_count}'
                    condition = m.group(1).strip()

                    loop = WhileProcedure.build(
                        name=loop_name,
                        _async=False,
                        requests=request_config[key],
                        condition=condition,
                        backend=backend,
                        id=id,
                    )

                    reqs.append(loop)
                    continue

            request_config['origin'] = Config.get('device_id')
            request_config['id'] = id
            if 'target' not in request_config:
                request_config['target'] = request_config['origin']

            request = Request.build(request_config)
            reqs.append(request)

        while not if_config.empty():
            pending_if = if_config.get()
            reqs.append(IfProcedure.build(**pending_if))

        return procedure_class(
            name=name,
            _async=_async,
            requests=reqs,
            args=args,
            backend=backend,
            **kwargs,
        )

    @staticmethod
    def _find_nearest_loop(stack):
        for proc in stack[::-1]:
            if isinstance(proc, LoopProcedure):
                return proc

        raise AssertionError('break/continue statement found outside of a loop')

    # pylint: disable=too-many-branches,too-many-statements
    def execute(self, n_tries=1, __stack__=None, **context):
        """
        Execute the requests in the procedure.

        :param n_tries: Number of tries in case of failure before raising a RuntimeError.
        """
        if not __stack__:
            __stack__ = [self]
        else:
            __stack__.append(self)

        if self.args:
            args = self.args.copy()
            for k, v in args.items():
                v = Request.expand_value_from_context(v, **context)
                args[k] = v
                context[k] = v
            logger.info('Executing procedure %s with arguments %s', self.name, args)
        else:
            logger.info('Executing procedure %s', self.name)

        response = Response()
        token = Config.get('token')

        for request in self.requests:
            if callable(request):
                response = request(**context)
                continue

            if isinstance(request, Statement):
                if request == Statement.RETURN:
                    self._should_return = True
                    for proc in __stack__:
                        proc._should_return = True  # pylint: disable=protected-access
                    break

                if request in [Statement.BREAK, Statement.CONTINUE]:
                    loop = self._find_nearest_loop(__stack__)
                    if request == Statement.BREAK:
                        loop._should_break = True  # pylint: disable=protected-access
                    else:
                        loop._should_continue = True  # pylint: disable=protected-access
                    break

            should_continue = getattr(self, '_should_continue', False)
            should_break = getattr(self, '_should_break', False)
            if isinstance(self, LoopProcedure) and (should_continue or should_break):
                if should_continue:
                    self._should_continue = (  # pylint: disable=attribute-defined-outside-init
                        False
                    )

                break

            if token and not isinstance(request, Statement):
                request.token = token

            context['_async'] = self._async
            context['n_tries'] = n_tries
            exec_ = getattr(request, 'execute', None)
            if callable(exec_):
                response = exec_(__stack__=__stack__, **context)

            if not self._async and response:
                if isinstance(response.output, dict):
                    for k, v in response.output.items():
                        context[k] = v

                context['output'] = response.output
                context['errors'] = response.errors

            if self._should_return:
                break

        return response or Response()

    def to_dict(self):
        return {
            'name': self.name,
            'requests': self.requests,
            'args': self.args,
            '_async': self._async,
        }


class LoopProcedure(Procedure):
    """
    Base class while and for/fork loops.
    """

    def __init__(self, name, requests, _async=False, args=None, backend=None):
        super().__init__(
            name=name, _async=_async, requests=requests, args=args, backend=backend
        )
        self._should_break = False
        self._should_continue = False


class ForProcedure(LoopProcedure):
    """
    Models a loop procedure, which expresses a construct similar to a
    for loop in a programming language. The 'for' keyword implies a synchronous
    loop, i.e. the nested actions will be executed in sequence. Use 'fork'
    instead of 'for' if you want to run the actions in parallel.

    Example::

        procedure.sync.process_results:
            - action: http.get
              args:
                  url: https://some-service/some/json/endpoint
                  # Example response: { "results": [ {"id":1, "name":"foo"}, {"id":2,"name":"bar"} ]}
            - for result in ${results}:
                - action: some.custom.action
                  args:
                      id: ${result['id']}
                      name: ${result['name']}

    """

    def __init__(
        self,
        name,
        iterator_name,
        iterable,
        requests,
        _async=False,
        args=None,
        backend=None,
    ):
        super().__init__(
            name=name, _async=_async, requests=requests, args=args, backend=backend
        )
        self.iterator_name = iterator_name
        self.iterable = iterable

    # pylint: disable=eval-used
    def execute(self, *_, **context):
        try:
            iterable = eval(self.iterable)
            assert hasattr(
                iterable, '__iter__'
            ), f'Object of type {type(iterable)} is not iterable: {iterable}'
        except Exception as e:
            logger.debug('Iterable %s expansion error: %s', self.iterable, e)
            iterable = Request.expand_value_from_context(self.iterable, **context)

        response = Response()

        for item in iterable:
            if self._should_return:
                logger.info('Returning from %s', self.name)
                break

            if self._should_continue:
                self._should_continue = False
                logger.info('Continuing loop %s', self.name)
                continue

            if self._should_break:
                self._should_break = False
                logger.info('Breaking loop %s', self.name)
                break

            context[self.iterator_name] = item
            response = super().execute(**context)

        return response


class WhileProcedure(LoopProcedure):
    """
    Models a while loop procedure.

    Example::

        procedure.process_results:
            - action: http.get
              args:
                  url: https://some-service/some/json/endpoint
                  # Example response: {"id":1, "name":"foo"}}

            - while ${output}:
                - action: some.custom.action
                  args:
                      id: ${id}
                      name: ${name}

                - action: http.get
                  args:
                      url: https://some-service/some/json/endpoint
                      # Example response: {"id":1, "name":"foo"}}

    """

    def __init__(
        self, name, condition, requests, _async=False, args=None, backend=None
    ):
        super().__init__(
            name=name, _async=_async, requests=requests, args=args, backend=backend
        )
        self.condition = condition

    @staticmethod
    def _get_context(**context):
        for k, v in context.items():
            try:
                context[k] = eval(v)  # pylint: disable=eval-used
            except Exception as e:
                logger.debug('Evaluation error for %s=%s: %s', k, v, e)
                if isinstance(v, str):
                    try:
                        context[k] = eval(  # pylint: disable=eval-used
                            '"' + re.sub(r'(^|[^\\])"', '\1\\"', v) + '"'
                        )
                    except Exception as ee:
                        logger.warning(
                            'Could not parse value for context variable %s=%s: %s',
                            k,
                            v,
                            ee,
                        )
                        logger.warning('Context: %s', context)
                        logger.exception(e)

        return context

    def execute(self, *_, **context):
        response = Response()
        context = self._get_context(**context)
        for k, v in context.items():
            locals()[k] = v

        while True:
            condition_true = eval(self.condition)  # pylint: disable=eval-used
            if not condition_true:
                break

            if self._should_return:
                logger.info('Returning from %s', self.name)
                break

            if self._should_continue:
                self._should_continue = False
                logger.info('Continuing loop %s', self.name)
                continue

            if self._should_break:
                self._should_break = False
                logger.info('Breaking loop %s', self.name)
                break

            response = super().execute(**context)

            if response.output and isinstance(response.output, dict):
                new_context = self._get_context(**response.output)
                for k, v in new_context.items():
                    locals()[k] = v

        return response


class IfProcedure(Procedure):
    """
    Models an if-else construct.

    Example::

        procedure.sync.process_results:
            - action: http.get
              args:
                url: https://some-service/some/json/endpoint
                # Example response: { "sensors": [ {"temperature": 18 } ] }

            - if ${sensors['temperature'] < 20}:
              - action: shell.exec
                args:
                  cmd: '/path/turn_on_heating.sh'
            - else:
              - action: shell.exec
                args:
                  cmd: '/path/turn_off_heating.sh'

    """

    def __init__(
        self,
        name,
        condition,
        requests,
        else_branch=None,
        args=None,
        backend=None,
        id=None,  # pylint: disable=redefined-builtin
        **kwargs,
    ):
        kwargs['_async'] = False
        self.condition = condition
        self.else_branch = else_branch
        reqs = []

        for req in requests:
            if isinstance(req, dict):
                req['origin'] = Config.get('device_id')
                req['id'] = id
                if 'target' not in req:
                    req['target'] = req['origin']

                req = Request.build(req)

            reqs.append(req)

        super().__init__(name=name, requests=reqs, args=args, backend=backend, **kwargs)

    @classmethod
    # pylint: disable=arguments-differ
    def build(
        cls,
        name,
        *_,
        condition,
        requests,
        args=None,
        backend=None,
        id=None,  # pylint: disable=redefined-builtin
        else_branch=None,
        **kwargs,
    ):
        kwargs['_async'] = False
        if else_branch:
            else_branch = super().build(
                name=name + '__else',
                requests=else_branch,
                args=args,
                backend=backend,
                id=id,
                procedure_class=Procedure,
                **kwargs,
            )

        return super().build(
            name=name,
            condition=condition,
            requests=requests,
            else_branch=else_branch,
            args=args,
            backend=backend,
            id=id,
            **kwargs,
        )

    def execute(self, *_, **context):
        for k, v in context.items():
            locals()[k] = v

        condition_true = eval(self.condition)  # pylint: disable=eval-used
        response = Response()

        if condition_true:
            response = super().execute(**context)
        elif self.else_branch:
            response = self.else_branch.execute(**context)

        return response


def procedure(name_or_func: Optional[str] = None, *upper_args, **upper_kwargs):
    name = name_or_func if isinstance(name_or_func, str) else None

    def func_wrapper(f):
        """
        Public decorator to mark a function as a procedure.
        """

        f.procedure = True
        f.procedure_name = name

        @wraps(f)
        def _execute_procedure(*args, **kwargs):
            args = [*upper_args, *args]
            kwargs = {**upper_kwargs, **kwargs}
            return exec_wrapper(f, *args, **kwargs)

        return _execute_procedure

    if callable(name_or_func):
        return func_wrapper(name_or_func)

    return func_wrapper


# vim:sw=4:ts=4:et:
