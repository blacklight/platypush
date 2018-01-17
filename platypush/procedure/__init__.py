import logging
import re

from ..config import Config
from ..message.request import Request
from ..message.response import Response

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

        logging.info('Executing request {}'.format(self.name))
        response = Response()

        for request in self.requests:
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

# vim:sw=4:ts=4:et:

