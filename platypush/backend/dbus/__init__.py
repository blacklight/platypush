from typing import Union

# noinspection PyPackageRequirements,PyUnresolvedReferences
from gi.repository import GLib

import dbus
import dbus.service
import dbus.mainloop.glib

from platypush.backend import Backend
from platypush.context import get_bus
from platypush.message import Message
from platypush.message.event import Event
from platypush.message.request import Request
from platypush.utils import run


# noinspection PyPep8Naming
class DBusService(dbus.service.Object):
    @classmethod
    def _parse_msg(cls, msg: Union[dict, list]):
        import json
        return Message.build(json.loads(json.dumps(msg)))

    @dbus.service.method('org.platypush.MessageBusInterface', in_signature='a{sv}', out_signature='v')
    def Post(self, msg: dict):
        """
        This method accepts a message as a dictionary (either representing a valid request or an event) and either
        executes it (request) or forwards it to the application bus (event).

        :param msg: Request or event, as a dictionary.
        :return: The return value of the request, or 0 if the message is an event.
        """
        msg = self._parse_msg(msg)
        if isinstance(msg, Request):
            ret = run(msg.action, **msg.args)
            if ret is None:
                ret = ''  # DBus doesn't like None return types

            return ret
        elif isinstance(msg, Event):
            get_bus().post(msg)
            return 0


class DbusBackend(Backend):
    """
    This backend acts as a proxy that receives messages (requests or events) on the DBus and forwards them to the
    application bus.

    The name of the messaging interface exposed by Platypush is ``org.platypush.MessageBusInterface`` and it exposes
    ``Post`` method, which accepts a dictionary representing a valid Platypush message (either a request or an event)
    and either executes it or forwards it to the application bus.

    Requires:

        * **dbus-python** (``pip install dbus-python``)

    """

    def __init__(self, bus_name='org.platypush.Bus', service_path='/MessageService', *args, **kwargs):
        """
        :param bus_name: Name of the bus where the application will listen for incoming messages (default:
            ``org.platypush.Bus``).
        :param service_path: Path to the service exposed by the app (default: ``/MessageService``).
        """
        super().__init__(*args, **kwargs)
        self.bus_name = bus_name
        self.service_path = service_path

    def run(self):
        super().run()

        # noinspection PyUnresolvedReferences
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        name = dbus.service.BusName(self.bus_name, bus)
        srv = DBusService(bus, self.service_path)

        loop = GLib.MainLoop()
        # noinspection PyProtectedMember
        self.logger.info('Starting DBus main loop - bus name: {}, service: {}'.format(name._name, srv._object_path))
        loop.run()


# vim:sw=4:ts=4:et:
