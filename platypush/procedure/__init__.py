import logging

from ..config import Config
from ..message.request import Request
from ..message.response import Response

class Procedure(object):
    """ Procedure class. A procedure is a pre-configured list of requests """

    def __init__(self, name, requests, backend=None):
        """
        Params:
            name     -- Procedure name
            requests -- List of platylist.message.request.Request objects
        """

        self.name     = name
        self.requests = requests
        self.backend  = backend

        for req in requests:
            req.backend = self.backend

    @classmethod
    def build(cls, name, requests, backend=None, id=None, **kwargs):
        reqs = []
        for request_config in requests:
            request_config['origin'] = Config.get('device_id')
            request_config['id'] = id
            if 'target' not in request_config:
                request_config['target'] = request_config['origin']

            request = Request.build(request_config)
            reqs.append(request)

        return cls(name=name, requests=reqs, backend=backend, **kwargs)

    def execute(self, n_tries=1):
        """
        Execute the requests in the procedure
        Params:
            n_tries -- Number of tries in case of failure before raising a RuntimeError
        """

        logging.info('Executing request {}'.format(self.name))
        context = {}
        response = Response()

        for request in self.requests:
            response = request.execute(n_tries, async=False, **context)
            context = { k:v for (k,v) in response.output.items() } \
                if isinstance(response.output, dict) else {}

            context['output'] = response.output
            context['errors'] = response.errors

        return response


# vim:sw=4:ts=4:et:

