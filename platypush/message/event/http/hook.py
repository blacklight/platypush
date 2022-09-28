import json
import uuid

from platypush.message.event import Event
from platypush.utils import get_redis


class WebhookEvent(Event):
    """
    Event triggered when a custom webhook is called.
    """

    def __init__(
        self,
        *argv,
        hook,
        method,
        data=None,
        args=None,
        headers=None,
        response=None,
        **kwargs,
    ):
        """
        :param hook: Name of the invoked web hook, from http://host:port/hook/<hook>
        :type hook: str

        :param method: HTTP method (in uppercase)
        :type method: str

        :param data: Extra data passed over POST/PUT/DELETE
        :type data: str or dict/list from JSON

        :param args: Extra query string arguments
        :type args: dict

        :param headers: Request headers
        :type args: dict

        :param response: Response returned by the hook.
        :type args: dict | list | str
        """
        # This queue is used to synchronize with the hook and wait for its completion
        kwargs['response_queue'] = kwargs.get(
            'response_queue', f'platypush/webhook/{str(uuid.uuid1())}'
        )

        super().__init__(
            *argv,
            hook=hook,
            method=method,
            data=data,
            args=args or {},
            headers=headers or {},
            response=response,
            **kwargs,
        )

    def send_response(self, response):
        output = response.output
        if isinstance(output, tuple):
            # A 3-sized tuple where the second element is an int and the third
            # is a dict represents an HTTP response in the format `(data,
            # http_code headers)`.
            if (
                len(output) == 3
                and isinstance(output[1], int)
                and isinstance(output[2], dict)
            ):
                output = {
                    '___data___': output[0],
                    '___code___': output[1],
                    '___headers___': output[2],
                }
            else:
                # Normalize tuples to lists before serialization
                output = list(output)
        if isinstance(output, (dict, list)):
            output = json.dumps(output)

        if output is None:
            output = ''
        get_redis().rpush(self.args['response_queue'], output)

    def wait_response(self, timeout=None):
        rs = get_redis().blpop(self.args['response_queue'], timeout=timeout)
        if rs and len(rs) > 1:
            return rs[1]


# vim:sw=4:ts=4:et:
