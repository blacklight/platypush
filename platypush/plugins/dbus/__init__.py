import enum
import json
from typing import Set, Dict, Optional
from xml.etree import ElementTree

import dbus

from platypush.plugins import Plugin, action


class BusType(enum.Enum):
    SYSTEM = 'system'
    SESSION = 'session'


class DbusPlugin(Plugin):
    """
    Plugin to interact with DBus.

    Requires:

        * **dbus-python** (``pip install dbus-python``)

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def _get_bus_names(bus: dbus.Bus) -> Set[str]:
        return set([str(name) for name in bus.list_names() if not name.startswith(':')])

    @classmethod
    def path_names(cls, bus: dbus.Bus, service: str, object_path='/', paths=None, service_dict=None):
        if not paths:
            paths = {}

        paths[object_path] = {}
        obj = bus.get_object(service, object_path)
        interface = dbus.Interface(obj, 'org.freedesktop.DBus.Introspectable')
        xml_string = interface.Introspect()
        root = ElementTree.fromstring(xml_string)

        for child in root:
            if child.tag == 'node':
                if object_path == '/':
                    object_path = ''
                new_path = '/'.join((object_path, child.attrib['name']))
                cls.path_names(bus, service, new_path, paths)
            else:
                if not object_path:
                    object_path = '/'
                function_dict = {}
                for func in list(child):
                    if func.tag not in function_dict.keys():
                        function_dict[func.tag] = []
                    function_dict[func.tag].append(func.attrib['name'])

                if function_dict:
                    paths[object_path][child.attrib['name']] = function_dict

        if not service_dict:
            service_dict = {}
        if paths:
            service_dict[service] = paths

        return service_dict

    @action
    def query(self, service: Optional[str] = None, system_bus: bool = True, session_bus: bool = True) \
            -> Dict[str, dict]:
        """
        Query DBus for a specific service or for the full list of services.

        :param service: Service name (default: None, query all services).
        :param system_bus: Query the system bus (default: True).
        :param session_bus: Query the session bus (default: True).
        :return: A ``{service_name -> {properties}}`` mapping.
        """
        busses = {}
        response = {}

        if system_bus:
            busses['system'] = dbus.SystemBus()
        if session_bus:
            busses['session'] = dbus.SessionBus()

        for bus_name, bus in busses.items():
            services = {}
            service_names = self._get_bus_names(bus)

            if not service:
                for srv in service_names:
                    services[srv] = self.path_names(bus, srv)
            elif service in service_names:
                services[service] = self.path_names(bus, service)

            response[bus_name] = services

        return response

    @action
    def execute(self, service: str, path: str, method_name: str, args: Optional[list] = None,
                interface: Optional[str] = None, bus_type: str = BusType.SESSION.value):
        """
        Execute a method exposed on DBus.

        :param service: Service/bus name (e.g. ``org.platypush.Bus``).
        :param path: Object path (e.g. ``/MessageService``).
        :param method_name: Method name (e.g. ``Post``).
        :param args: Arguments to be passed to the method, depending on the method signature.
        :param interface: Interface name (e.g. ``org.platypush.MessageBusInterface``).
        :param bus_type: Bus type (supported: ``system`` and ``session`` - default: ``session``).
        :return: Return value of the executed method.
        """
        if not args:
            args = []

        kwargs = {}
        if interface:
            kwargs['dbus_interface'] = interface

        bus_type = BusType(bus_type)
        bus = dbus.SessionBus() if bus_type == BusType.SESSION else dbus.SystemBus()
        obj = bus.get_object(bus_name=service, object_path=path)
        ret = getattr(obj, method_name)(*args, **kwargs)
        return json.loads(json.dumps(ret))


# vim:sw=4:ts=4:et:
