import enum
import logging
import re
from copy import deepcopy
from dataclasses import dataclass, field
from functools import wraps

from queue import LifoQueue
from typing import Any, Dict, Iterable, List, Optional

from ..common import exec_wrapper
from ..config import Config
from ..message.request import Request
from ..message.response import Response

logger = logging.getLogger('platypush')


class StatementType(enum.Enum):
    """
    Enumerates the possible statements in a procedure.
    """

    BREAK = 'break'
    CONTINUE = 'continue'
    RETURN = 'return'
    SET = 'set'


@dataclass
class Statement:
    """
    Models a statement in a procedure.
    """

    type: StatementType
    argument: Optional[Any] = None

    @classmethod
    def build(cls, statement: str):
        """
        Builds a statement from a string.
        """

        m = re.match(r'\s*return\s*(.*)\s*', statement, re.IGNORECASE)
        if m:
            return ReturnStatement(argument=m.group(1))

        return cls(StatementType(statement.lower()))

    def run(self, *_, **__) -> Optional[Any]:
        """
        Executes the statement.
        """


@dataclass
class ReturnStatement(Statement):
    """
    Models a return statement in a procedure.
    """

    type: StatementType = StatementType.RETURN

    def run(self, *_, **context) -> Any:
        return Response(
            output=Request.expand_value_from_context(
                self.argument, **_update_context(context)
            )
        )


@dataclass
class SetStatement(Statement):
    """
    Models a set variable statement in a procedure.
    """

    type: StatementType = StatementType.SET
    vars: dict = field(default_factory=dict)

    def run(self, *_, **context):
        vars = deepcopy(self.vars)  # pylint: disable=redefined-builtin
        for k, v in vars.items():
            vars[k] = Request.expand_value_from_context(v, **context)

        context.update(vars)
        return Response(output=vars)


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
        kwargs.pop('id', None)

        for request_config in requests:
            # Check if it's a break/continue/return statement
            if isinstance(request_config, str):
                cls._flush_if_statements(reqs, if_config)
                reqs.append(Statement.build(request_config))
                continue

            # Check if it's a return statement with a value
            if (
                len(request_config.keys()) == 1
                and list(request_config.keys())[0] == StatementType.RETURN.value
            ):
                cls._flush_if_statements(reqs, if_config)
                reqs.append(
                    ReturnStatement(argument=request_config[StatementType.RETURN.value])
                )
                continue

            # Check if it's a variable set statement
            if (len(request_config.keys()) == 1) and (
                list(request_config.keys())[0] == StatementType.SET.value
            ):
                cls._flush_if_statements(reqs, if_config)
                reqs.append(SetStatement(vars=request_config[StatementType.SET.value]))
                continue

            # Check if this request is an if-else
            if len(request_config.keys()) >= 1:
                key = list(request_config.keys())[0]
                m = re.match(r'\s*(if)\s+\${(.*)}\s*', key)

                if m:
                    cls._flush_if_statements(reqs, if_config)
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
                    )

                    reqs.append(loop)
                    continue

            request_config['origin'] = Config.get('device_id')
            if 'target' not in request_config:
                request_config['target'] = request_config['origin']

            request = Request.build(request_config)
            reqs.append(request)

        cls._flush_if_statements(reqs, if_config)

        return procedure_class(
            name=name,
            _async=_async,
            requests=reqs,
            args=args,
            backend=backend,
            **kwargs,
        )

    @staticmethod
    def _flush_if_statements(requests: List, if_config: LifoQueue):
        while not if_config.empty():
            pending_if = if_config.get()
            requests.append(IfProcedure.build(**pending_if))

    # pylint: disable=too-many-branches,too-many-statements
    def execute(
        self,
        n_tries: int = 1,
        __stack__: Optional[Iterable] = None,
        new_context: Optional[Dict[str, Any]] = None,
        **context,
    ):
        """
        Execute the requests in the procedure.

        :param n_tries: Number of tries in case of failure before raising a RuntimeError.
        """
        __stack__ = (self,) if not __stack__ else (self, *__stack__)
        new_context = new_context or {}

        if self.args:
            args = self.args.copy()
            for k, v in args.items():
                args[k] = context[k] = Request.expand_value_from_context(v, **context)
            logger.info('Executing procedure %s with arguments %s', self.name, args)
        else:
            logger.info('Executing procedure %s', self.name)

        response = Response()
        token = Config.get('token')
        context = _update_context(context)
        locals().update(context)

        # pylint: disable=too-many-nested-blocks
        for request in self.requests:
            if callable(request):
                response = request(**context)
                continue

            context['_async'] = self._async
            context['n_tries'] = n_tries
            context['__stack__'] = __stack__
            context['new_context'] = new_context

            if isinstance(request, Statement):
                if isinstance(request, ReturnStatement):
                    response = request.run(**context)
                    self._should_return = True
                    for proc in __stack__:
                        proc._should_return = True  # pylint: disable=protected-access

                    break

                if isinstance(request, SetStatement):
                    rs: dict = request.run(**context).output  # type: ignore
                    context.update(rs)
                    new_context.update(rs)
                    locals().update(rs)
                    continue

                if request.type in [StatementType.BREAK, StatementType.CONTINUE]:
                    for proc in __stack__:
                        if isinstance(proc, LoopProcedure):
                            if request.type == StatementType.BREAK:
                                setattr(proc, '_should_break', True)  # noqa: B010
                            else:
                                setattr(proc, '_should_continue', True)  # noqa: B010
                            break

                        proc._should_return = True  # pylint: disable=protected-access

                    break

            should_continue = getattr(self, '_should_continue', False)
            should_break = getattr(self, '_should_break', False)
            if self._should_return or should_continue or should_break:
                break

            if token and not isinstance(request, Statement):
                request.token = token

            exec_ = getattr(request, 'execute', None)
            if callable(exec_):
                response = exec_(**context)
                context.update(context.get('new_context', {}))

            if not self._async and response:
                if isinstance(response.output, dict):
                    context.update(response.output)

                context['output'] = response.output
                context['errors'] = response.errors
                new_context.update(context)
                locals().update(context)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        ctx = _update_context(context)
        locals().update(ctx)

        try:
            iterable = eval(self.iterable)
            assert hasattr(
                iterable, '__iter__'
            ), f'Object of type {type(iterable)} is not iterable: {iterable}'
        except Exception as e:
            logger.debug('Iterable %s expansion error: %s', self.iterable, e)
            iterable = Request.expand_value_from_context(self.iterable, **ctx)

        response = Response()

        for item in iterable:
            ctx[self.iterator_name] = item
            response = super().execute(**ctx)
            ctx.update(ctx.get('new_context', {}))

            if response.output and isinstance(response.output, dict):
                ctx = _update_context(ctx, **response.output)

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

    def execute(self, *_, **context):
        response = Response()
        ctx = _update_context(context)
        locals().update(ctx)

        while True:
            condition_true = eval(self.condition)  # pylint: disable=eval-used
            if not condition_true:
                break

            response = super().execute(**ctx)
            ctx.update(ctx.get('new_context', {}))
            if response.output and isinstance(response.output, dict):
                _update_context(ctx, **response.output)

            locals().update(ctx)

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
        ctx = _update_context(context)
        locals().update(ctx)
        condition_true = eval(self.condition)  # pylint: disable=eval-used
        response = Response()

        if condition_true:
            response = super().execute(**ctx)
        elif self.else_branch:
            response = self.else_branch.execute(**ctx)

        return response


def _update_context(context: Optional[Dict[str, Any]] = None, **kwargs):
    ctx = context or {}
    ctx = {**ctx.get('context', {}), **ctx, **kwargs}
    for k, v in ctx.items():
        ctx[k] = Request.expand_value_from_context(v, **ctx)

    return ctx


def procedure(name_or_func: Optional[str] = None, *upper_args, **upper_kwargs):
    name = name_or_func if isinstance(name_or_func, str) else None

    def func_wrapper(f):
        """
        Public decorator to mark a function as a procedure.
        """
        import inspect

        f.procedure = True
        f.procedure_name = name
        f._source = inspect.getsourcefile(f)  # pylint: disable=protected-access
        f._line = inspect.getsourcelines(f)[1]  # pylint: disable=protected-access

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
