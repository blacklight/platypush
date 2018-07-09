import logging
import re

from ..config import Config
from ..message.request import Request
from ..message.response import Response

logger = logging.getLogger(__name__)


class Procedure(object):
    """ Procedure class. A procedure is a pre-configured list of requests """

    def __init__(self, name, async, requests, backend=None):
        """
        Params:
            name     -- Procedure name
            async    -- Whether the actions in the procedure are supposed to
                        be executed sequentially or in parallel (True or False)
            requests -- List of platylist.message.request.Request objects
        """

        self.name     = name
        self.async    = async
        self.requests = requests
        self.backend  = backend

        for req in requests:
            req.backend = self.backend


    @classmethod
    def build(cls, name, async, requests, backend=None, id=None, **kwargs):
        reqs = []
        loop_count = 0
        if_count = 0

        for request_config in requests:
            # Check if this request is a for loop
            if len(request_config.keys()) == 1:
                key = list(request_config.keys())[0]
                m = re.match('\s*(fork?)\s+([\w\d_]+)\s+in\s+(.*)\s*', key)

                if m:
                    loop_count += 1
                    loop_name = '{}__loop_{}'.format(name, loop_count)

                    # A 'for' loop is synchronous. Declare a 'fork' loop if you
                    # want to process the elements in the iterable in parallel
                    async = True if m.group(1) == 'fork' else False
                    iterator_name = m.group(2)
                    iterable = m.group(3)

                    loop = LoopProcedure.build(name=loop_name, async=async,
                                               requests=request_config[key],
                                               backend=backend, id=id,
                                               iterator_name=iterator_name,
                                               iterable=iterable)

                    reqs.append(loop)
                    continue

            # Check if this request is an if-else
            if len(request_config.keys()) >= 1:
                key = list(request_config.keys())[0]
                m = re.match('\s*(if)\s+\$\{(.*)\}\s*', key)
                if m:
                    if_count += 1
                    if_name = '{}__if_{}'.format(name, if_count)
                    condition = m.group(2)
                    else_branch = request_config['else'] if 'else' in request_config else []

                    if_proc = IfProcedure(name=if_name,
                                          requests=request_config[key],
                                          condition=condition,
                                          else_branch=else_branch,
                                          backend=backend, id=id)

                    reqs.append(if_proc)
                    continue

            request_config['origin'] = Config.get('device_id')
            request_config['id'] = id
            if 'target' not in request_config:
                request_config['target'] = request_config['origin']

            request = Request.build(request_config)
            reqs.append(request)

        return cls(name=name, async=async, requests=reqs, backend=backend, **kwargs)


    def execute(self, n_tries=1, **context):
        """
        Execute the requests in the procedure
        Params:
            n_tries -- Number of tries in case of failure before raising a RuntimeError
        """

        logger.info('Executing request {}'.format(self.name))
        response = Response()
        token = Config.get('token')

        for request in self.requests:
            if token:
                request.token = token

            context['async'] = self.async; context['n_tries'] = n_tries
            response = request.execute(**context)

            if not self.async:
                if isinstance(response.output, dict):
                    for (k,v) in response.output.items():
                        context[k] = v

                context['output'] = response.output
                context['errors'] = response.errors

        return response


class LoopProcedure(Procedure):
    """
    Models a loop procedure, which expresses a construct similar to a
    for loop in a programming language. The 'for' keyword implies a synchronous
    loop, i.e. the nested actions will be executed in sequence. Use 'fork'
    instead of 'for' if you want to run the actions in parallel.

    Example:

        procedure.sync.process_results:
            -
                action: http.get
                args:
                    url: https://some-service/some/json/endpoint
                    # Example response: { "results": [ {"id":1, "name":"foo"}, {"id":2,"name":"bar"} ]}
            -
                for result in ${results}:
                    -
                        action: some.custom.action
                        args:
                            id: ${result['id']}
                            name: ${result['name']}
    """

    context = {}

    def __init__(self, name, iterator_name, iterable, requests, async=False, backend=None, **kwargs):
        super(). __init__(name=name, async=async, requests=requests, backend=None, **kwargs)

        self.iterator_name = iterator_name
        self.iterable = iterable
        self.requests = requests


    def execute(self, async=None, **context):
        iterable = Request.expand_value_from_context(self.iterable, **context)
        response = Response()

        for item in iterable:
            context[self.iterator_name] = item
            response = super().execute(**context)

        return response


class IfProcedure(Procedure):
    """
    Models an if-else construct.

    Example:

        procedure.sync.process_results:
            -
                action: http.get
                args:
                    url: https://some-service/some/json/endpoint
                    # Example response: { "sensors": [ {"temperature": 18 } ] }
            -
                if ${sensors['temperature'] < 20}:
                    -
                        action: shell.exec
                        args:
                            cmd: '/path/turn_on_heating.sh'
                else:
                    -
                        action: shell.exec
                        args:
                            cmd: '/path/turn_off_heating.sh'
    """

    context = {}

    def __init__(self, name, condition, requests, else_branch=[], backend=None, id=None, **kwargs):
        kwargs['async'] = False
        self.condition = condition
        self.else_branch = []
        reqs = []

        for req in requests:
            req['origin'] = Config.get('device_id')
            req['id'] = id
            if 'target' not in req:
                req['target'] = req['origin']

            reqs.append(Request.build(req))

        for req in else_branch:
            req['origin'] = Config.get('device_id')
            req['id'] = id
            if 'target' not in req:
                req['target'] = req['origin']

            self.else_branch.append(Request.build(req))

        super(). __init__(name=name, requests=reqs, backend=None, **kwargs)


    def execute(self, **context):
        for (k, v) in context.items():
            try:
                exec('{}={}'.format(k, v))
            except:
                if isinstance(v, str):
                    try:
                        exec('{}="{}"'.format(k, re.sub('(^|[^\\\])"', '\1\\"', v)))
                    except:
                        pass

        condition_true = eval(self.condition)
        response = Response()

        if condition_true:
            response = super().execute(**context)
        elif self.else_branch:
            try:
                reqs = self.requests
                self.requests = self.else_branch
                response = super().execute(**context)
            finally:
                self.requests = reqs

        return response


# vim:sw=4:ts=4:et:

