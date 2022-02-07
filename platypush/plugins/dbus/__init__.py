import enum
import json
from typing import Set, Dict, Optional, Iterable, Callable, Union

from gi.repository import GLib   # type: ignore
from pydbus import SessionBus, SystemBus
from pydbus.bus import Bus
from defusedxml import ElementTree

from platypush.context import get_bus
from platypush.message import Message
from platypush.message.event import Event
from platypush.message.event.dbus import DbusSignalEvent
from platypush.message.request import Request
from platypush.plugins import RunnablePlugin, action
from platypush.schemas.dbus import DbusSignalSchema
from platypush.utils import run


_default_service_name = 'org.platypush.Bus'
_default_service_path = '/'
_default_interface_name = 'org.platypush.Bus'


class BusType(enum.Enum):
    SYSTEM = 'system'
    SESSION = 'session'


class DBusService():
    """
    <node>
      <interface name="org.platypush.Bus">
        <method name="Post">
          <arg type="s" name="msg" direction="in"/>
          <arg type="s" name="response" direction="out"/>
        </method>
      </interface>
    </node>
    """

    @classmethod
    def _parse_msg(cls, msg: Union[str, dict]) -> dict:
        return Message.build(json.loads(json.dumps(msg)))

    def Post(self, msg: dict):
        """
        This method accepts a message as a JSON object
        (either representing a valid request or an event) and either
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

        if isinstance(msg, Event):
            get_bus().post(msg)
            return 0


class DbusPlugin(RunnablePlugin):
    """
    Plugin to interact with DBus.

    This plugin can be used for the following tasks:

        * It can expose a D-Bus interface that other applications can use to push messages
          to Platypush (either action requests or events) serialized in JSON format.
          You can disable this listener by setting ``service_name`` to ``null`` in your
          configuration. If the D-Bus Platypush interface is enabled then you can push
          Platypush events and requests in JSON format from another application or script
          by specifying:

              * The D-Bus service (default: ``org.platypush.Bus``)
              * The D-Bus interface (default: ``org.platypush.Bus``)
              * The D-Bus path (default: ``/``)
              * The D-Bus method (``Post``)
              * The Platypush JSON payload (first argument of the request). Format:
                ``{"type": "request", "action": "module.action", "args": {...}}``

        * It can subscribe to multiple D-Bus signals, and it triggers a ``DbusSignalEvent``
          when an event is received (signal filters should be specified in the ``signals``
          configuration).

        * It can be used to query and inspect D-Bus objects through the :meth:`.query` method.

        * It can be used to execute methods exponsed by D-Bus objects through the
          :meth:`.execute` method.

    Requires:

        * **pydbus** (``pip install pydbus``)
        * **defusedxml** (``pip install defusedxml``)

    Triggers:

        * :class:`platypush.message.event.dbus.DbusSignalEvent` when a signal is received.

    """

    def __init__(
            self, signals: Optional[Iterable[dict]] = None,
            service_name: Optional[str] = _default_service_name,
            service_path: Optional[str] = _default_service_path, **kwargs
    ):
        """
        :param signals: Specify this if you want to subscribe to specific DBus
            signals. Structure:

            .. schema:: dbus.DbusSignalSchema(many=True)

            For example, to subscribe to all the messages on the session bus:

            .. code-block:: yaml

                dbus:
                    signals:
                        - bus: session

        :param service_name: Name of the D-Bus service where Platypush will listen
            for new messages (requests and events). Set to null if you want to disable
            message execution over D-Bus for Platypush (default: ``org.platypush.Bus``).

        :param service_path: The path of the D-Bus message listener. Set to null
            if you want to disable message execution over D-Bus for Platypush
            (default: ``/``).
        """
        super().__init__(**kwargs)
        self._system_bus = SystemBus()
        self._session_bus = SessionBus()
        self._loop = None
        self._signals = DbusSignalSchema().load(signals or [], many=True)
        self._signal_handlers = [
            self._get_signal_handler(**signal)
            for signal in self._signals
        ]

        self.service_name = service_name
        self.service_path = service_path

    @staticmethod
    def _get_signal_handler(bus: str, **_) -> Callable:
        def handler(sender, path, interface, signal, params):
            get_bus().post(
                DbusSignalEvent(
                    bus=bus, signal=signal, path=path,
                    interface=interface, sender=sender, params=params
                )
            )

        return handler

    def _get_bus(self, bus_type: Union[str, BusType]) -> Bus:
        if isinstance(bus_type, str):
            bus_type = BusType(bus_type.lower())
        return self._system_bus if bus_type == BusType.SYSTEM else self._session_bus

    def _init_signal_listeners(self):
        for i, signal in enumerate(self._signals):
            handler = self._signal_handlers[i]
            bus = self._get_bus(signal['bus'])
            bus.subscribe(
                signal_fired=handler,
                signal=signal.get('signal'),
                sender=signal.get('sender'),
                object=signal.get('path'),
                iface=signal.get('interface'),
            )

    def _init_service(self):
        if not (self.service_name and self.service_path):
            return

        self._session_bus.publish(
            self.service_name,
            ('/', DBusService()),
        )

    def main(self):
        self._init_signal_listeners()
        self._init_service()

        self._loop = GLib.MainLoop()
        self._loop.run()

    def stop(self):
        self._should_stop.set()
        if self._loop:
            self._loop.quit()
            self._loop = None
            self.logger.info('Stopped D-Bus main loop')

    @staticmethod
    def _get_bus_names(bus: Bus) -> Set[str]:
        return {str(name) for name in bus.dbus.ListNames() if not name.startswith(':')}

    def path_names(self, bus: Bus, service: str, object_path='/', paths=None, service_dict=None):
        if paths is None:
            paths = {}
        if service_dict is None:
            service_dict = {}

        paths[object_path] = {}
        try:
            obj = bus.get(service, object_path)
            interface = obj['org.freedesktop.DBus.Introspectable']
        except GLib.GError as e:
            self.logger.warning(f'Could not inspect D-Bus object {service}, path={object_path}: {e}')
            return {}
        except KeyError as e:
            self.logger.warning(f'Could not get interfaces on the D-Bus object {service}, path={object_path}: {e}')
            return {}

        xml_string = interface.Introspect()
        root = ElementTree.fromstring(xml_string)

        for child in root:
            if child.tag == 'node':
                if object_path == '/':
                    object_path = ''
                new_path = '/'.join((object_path, child.attrib['name']))
                self.path_names(bus, service, new_path, paths, service_dict=service_dict)
            else:
                if not object_path:
                    object_path = '/'
                functions_dict = {}
                for func in list(child):
                    function_dict = {'name': func.attrib['name']}
                    for arg in list(func):
                        if arg.tag != 'arg':
                            continue

                        function_dict['args'] = function_dict.get('args', [])
                        function_dict['args'].append(arg.attrib)

                    if func.tag not in functions_dict:
                        functions_dict[func.tag] = []
                    functions_dict[func.tag].append(function_dict)

                if functions_dict:
                    paths[object_path][child.attrib['name']] = functions_dict

        if paths:
            service_dict[service] = paths

        return service_dict

    @action
    def query(self, service: Optional[str] = None, bus=tuple(t.value for t in BusType)) \
            -> Dict[str, dict]:
        """
        Query DBus for a specific service or for the full list of services.

        :param service: Service name (default: None, query all services).
        :param bus: Which bus(ses) should be queried (default: both ``system`` and ``session``).
        :return: A ``{service_name -> {properties}}`` mapping. Example:

            .. code-block:: json

              "session": {
                "org.platypush.Bus": {
                  "/": {
                    "org.freedesktop.DBus.Properties": {
                      "method": [
                        {
                          "name": "Get",
                          "args": [
                            {
                              "type": "s",
                              "name": "interface_name",
                              "direction": "in"
                            },
                            {
                              "type": "s",
                              "name": "property_name",
                              "direction": "in"
                            },
                            {
                              "type": "v",
                              "name": "value",
                              "direction": "out"
                            }
                          ]
                        },
                        {
                          "name": "GetAll",
                          "args": [
                            {
                              "type": "s",
                              "name": "interface_name",
                              "direction": "in"
                            },
                            {
                              "type": "a{sv}",
                              "name": "properties",
                              "direction": "out"
                            }
                          ]
                        },
                        {
                          "name": "Set",
                          "args": [
                            {
                              "type": "s",
                              "name": "interface_name",
                              "direction": "in"
                            },
                            {
                              "type": "s",
                              "name": "property_name",
                              "direction": "in"
                            },
                            {
                              "type": "v",
                              "name": "value",
                              "direction": "in"
                            }
                          ]
                        }
                      ],
                      "signal": [
                        {
                          "name": "PropertiesChanged",
                          "args": [
                            {
                              "type": "s",
                              "name": "interface_name"
                            },
                            {
                              "type": "a{sv}",
                              "name": "changed_properties"
                            },
                            {
                              "type": "as",
                              "name": "invalidated_properties"
                            }
                          ]
                        }
                      ]
                    },
                    "org.freedesktop.DBus.Introspectable": {
                      "method": [
                        {
                          "name": "Introspect",
                          "args": [
                            {
                              "type": "s",
                              "name": "xml_data",
                              "direction": "out"
                            }
                          ]
                        }
                      ]
                    },
                    "org.freedesktop.DBus.Peer": {
                      "method": [
                        {
                          "name": "Ping"
                        },
                        {
                          "name": "GetMachineId",
                          "args": [
                            {
                              "type": "s",
                              "name": "machine_uuid",
                              "direction": "out"
                            }
                          ]
                        }
                      ]
                    },
                    "org.platypush.Bus": {
                      "method": [
                        {
                          "name": "Post",
                          "args": [
                            {
                              "type": "s",
                              "name": "msg",
                              "direction": "in"
                            },
                            {
                              "type": "s",
                              "name": "response",
                              "direction": "out"
                            }
                          ]
                        }
                      ]
                    }
                  }
                }
              }

        """
        busses = {}
        response = {}

        if isinstance(bus, str):
            bus = (bus,)

        if BusType.SYSTEM.value in bus:
            busses['system'] = self._system_bus
        if BusType.SESSION.value in bus:
            busses['session'] = self._session_bus

        for bus_name, bus in busses.items():
            services = {}
            service_names = self._get_bus_names(bus)

            if not service:
                for srv in service_names:
                    services.update(self.path_names(bus, srv))
            elif service in service_names:
                services.update(self.path_names(bus, service))

            response[bus_name] = services

        return response

    @action
    def execute(
            self,
            service: str,
            interface: str,
            method_name: str,
            bus: str = BusType.SESSION.value,
            path: str = '/',
            args: Optional[list] = None
    ):
        """
        Execute a method exposed on DBus.

        :param service: D-Bus service name.
        :param interface: D-Bus nterface name.
        :param method_name: Method name.
        :param bus: Bus type. Supported: ``system`` and ``session`` (default: ``session``).
        :param path: Object path.
        :param args: Arguments to be passed to the method, depending on the method signature.
        :return: Return value of the executed method.
        """
        if not args:
            args = []

        bus = self._get_bus(bus)
        obj = bus.get(service, path)[interface]
        method = getattr(obj, method_name, None)
        assert method, (
            f'No such method exposed by service={service}, '
            f'interface={interface}: {method_name}'
        )

        # Normalize any lists/dictionaries to JSON strings
        for i, arg in enumerate(args):
            if isinstance(arg, (list, tuple, dict)):
                args[i] = json.dumps(arg)

        ret = method(*args)

        try:
            ret = json.loads(json.dumps(ret))
        except Exception as e:
            self.logger.debug(e)

        return ret


# vim:sw=4:ts=4:et:
