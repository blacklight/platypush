from platypush.context import get_backend
from platypush.message.response import Response

from .. import Plugin

class SerialPlugin(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_data(self):
        backend = get_backend('serial')
        return Response(output=backend.get_data())


# vim:sw=4:ts=4:et:

