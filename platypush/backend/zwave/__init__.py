import inspect
import logging
import queue
import os
import threading

from typing import Optional

from platypush.backend import Backend
from platypush.config import Config
from platypush.message.event.zwave import ZwaveNetworkReadyEvent, ZwaveNetworkStoppedEvent, ZwaveEvent, \
    ZwaveNodeAddedEvent, ZwaveValueAddedEvent, ZwaveNodeQueryCompletedEvent, ZwaveValueChangedEvent, \
    ZwaveValueRefreshedEvent, ZwaveValueRemovedEvent, ZwaveNetworkResetEvent, ZwaveCommandEvent, \
    ZwaveCommandWaitingEvent, ZwaveNodeRemovedEvent, ZwaveNodeRenamedEvent, ZwaveNodeReadyEvent, \
    ZwaveButtonRemovedEvent, ZwaveButtonCreatedEvent, ZwaveButtonOnEvent, ZwaveButtonOffEvent, ZwaveNetworkErrorEvent, \
    ZwaveNodeGroupEvent, ZwaveNodePollingEnabledEvent, ZwaveNodePollingDisabledEvent, ZwaveNodeSceneEvent, \
    ZwaveNodeEvent

event_queue = queue.Queue()
network_ready = threading.Event()


class _ZWEvent:
    def __init__(self, signal: str, sender: str, network=None, **kwargs):
        self.signal = signal
        self.sender = sender
        self.network = network
        self.args = kwargs


def _zwcallback(signal, sender, network, **kwargs):
    if signal == network.SIGNAL_NETWORK_AWAKED:
        network_ready.set()
    event_queue.put(_ZWEvent(signal=signal, sender=sender, network=network, **kwargs))


class ZwaveBackend(Backend):
    """
    Start and manage a Z-Wave network.

    If you are using a USB adapter and want a consistent naming for the device paths, you can use udev.

    .. code-block:: shell

        # Get the vendorID and productID of your device through lsusb.
        # Then add a udev rule for it to link it e.g. to /dev/zwave.

        cat <<EOF > /etc/udev/rules.d/92-zwave.rules
        SUBSYSTEM=="tty", ATTRS{idVendor}=="0658", ATTRS{idProduct}=="0200", SYMLINK+="zwave"
        EOF

        # Restart the udev service
        systemctl restart systemd-udevd.service

    Triggers:

        * :class:`platypush.message.event.zwave.ZwaveNetworkReadyEvent` when the network is up and running.
        * :class:`platypush.message.event.zwave.ZwaveNetworkStoppedEvent` when the network goes down.
        * :class:`platypush.message.event.zwave.ZwaveNetworkResetEvent` when the network is reset.
        * :class:`platypush.message.event.zwave.ZwaveNetworkErrorEvent` when an error occurs on the network.
        * :class:`platypush.message.event.zwave.ZwaveNodeQueryCompletedEvent` when all the nodes on the network
          have been queried.
        * :class:`platypush.message.event.zwave.ZwaveNodeEvent` when a node attribute changes.
        * :class:`platypush.message.event.zwave.ZwaveNodeAddedEvent` when a node is added to the network.
        * :class:`platypush.message.event.zwave.ZwaveNodeRemovedEvent` when a node is removed from the network.
        * :class:`platypush.message.event.zwave.ZwaveNodeRenamedEvent` when a node is renamed.
        * :class:`platypush.message.event.zwave.ZwaveNodeReadyEvent` when a node is ready.
        * :class:`platypush.message.event.zwave.ZwaveNodeGroupEvent` when a node is associated/de-associated to a
          group.
        * :class:`platypush.message.event.zwave.ZwaveNodeSceneEvent` when a scene is set on a node.
        * :class:`platypush.message.event.zwave.ZwaveNodePollingEnabledEvent` when the polling is successfully turned
          on a node.
        * :class:`platypush.message.event.zwave.ZwaveNodePollingDisabledEvent` when the polling is successfully turned
          off a node.
        * :class:`platypush.message.event.zwave.ZwaveButtonCreatedEvent` when a button is added to the network.
        * :class:`platypush.message.event.zwave.ZwaveButtonRemovedEvent` when a button is removed from the network.
        * :class:`platypush.message.event.zwave.ZwaveButtonOnEvent` when a button is pressed.
        * :class:`platypush.message.event.zwave.ZwaveButtonOffEvent` when a button is released.
        * :class:`platypush.message.event.zwave.ZwaveValueAddedEvent` when a value is added to a node on the network.
        * :class:`platypush.message.event.zwave.ZwaveValueChangedEvent` when the value of a node on the network
          changes.
        * :class:`platypush.message.event.zwave.ZwaveValueRefreshedEvent` when the value of a node on the network
          is refreshed.
        * :class:`platypush.message.event.zwave.ZwaveValueRemovedEvent` when the value of a node on the network
          is removed.
        * :class:`platypush.message.event.zwave.ZwaveCommandEvent` when a command is received on the network.
        * :class:`platypush.message.event.zwave.ZwaveCommandWaitingEvent` when a command is waiting for a message
          to complete.

    Requires:

        * **python-openzwave** (``pip install python-openzwave``)

    """

    def __init__(self, device: str, config_path: Optional[str] = None, user_path: Optional[str] = None,
                 ready_timeout: float = 10.0, *args, **kwargs):
        """
        :param device: Path to the Z-Wave adapter (e.g. /dev/ttyUSB0 or /dev/ttyACM0).
        :param config_path: Z-Wave configuration path (default: ``<OPENZWAVE_PATH>/ozw_config``).
        :param user_path: Z-Wave user path where runtime and configuration files will be stored
            (default: ``<PLATYPUSH_WORKDIR>/zwave``).
        :param ready_timeout: Network ready timeout in seconds (default: 60).
        """
        import python_openzwave
        from openzwave.network import ZWaveNetwork

        super().__init__(*args, **kwargs)
        self.device = device

        if not config_path:
            # noinspection PyTypeChecker
            config_path = os.path.join(os.path.dirname(inspect.getfile(python_openzwave)), 'ozw_config')
        if not user_path:
            user_path = os.path.join(Config.get('workdir'), 'zwave')
            os.makedirs(user_path, mode=0o770, exist_ok=True)

        self.config_path = config_path
        self.user_path = user_path
        self.ready_timeout = ready_timeout
        self.network: Optional[ZWaveNetwork] = None

    def start_network(self):
        if self.network and self.network.state >= self.network.STATE_AWAKED:
            self.logger.info('Z-Wave network already started')
            return

        from openzwave.network import ZWaveNetwork, dispatcher
        from openzwave.option import ZWaveOption

        network_ready.clear()
        logging.getLogger('openzwave').addHandler(self.logger)
        opts = ZWaveOption(self.device, config_path=self.config_path, user_path=self.user_path)
        opts.set_console_output(False)
        opts.lock()

        self.network = ZWaveNetwork(opts, log=None)
        dispatcher.connect(_zwcallback)
        ready = network_ready.wait(self.ready_timeout)

        if not ready:
            self.logger.warning('Driver not ready after {} seconds: continuing anyway'.format(self.ready_timeout))

    def stop_network(self):
        if self.network:
            self.network.stop()
            network_ready.clear()
            self.network = None

    def _process_event(self, event: _ZWEvent):
        from platypush.plugins.zwave import ZwavePlugin
        network = event.network if hasattr(event, 'network') and event.network else self.network

        if event.signal == network.SIGNAL_NETWORK_STOPPED or \
                event.signal == network.SIGNAL_DRIVER_REMOVED:
            event = ZwaveNetworkStoppedEvent(device=self.device)
        elif event.signal == network.SIGNAL_ALL_NODES_QUERIED or \
                event.signal == network.SIGNAL_ALL_NODES_QUERIED_SOME_DEAD:
            event = ZwaveNodeQueryCompletedEvent(device=self.device)
        elif event.signal == network.SIGNAL_NETWORK_FAILED:
            event = ZwaveNetworkErrorEvent(device=self.device)
            self.logger.warning('Z-Wave network error')
        elif event.signal == network.SIGNAL_NETWORK_RESETTED or \
                event.signal == network.SIGNAL_DRIVER_RESET:
            event = ZwaveNetworkResetEvent(device=self.device)
        elif event.signal == network.SIGNAL_BUTTON_ON:
            event = ZwaveButtonOnEvent(device=self.device,
                                       node=ZwavePlugin.node_to_dict(event.args['node']))
        elif event.signal == network.SIGNAL_BUTTON_OFF:
            event = ZwaveButtonOffEvent(device=self.device,
                                        node=ZwavePlugin.node_to_dict(event.args['node']))
        elif event.signal == network.SIGNAL_CONTROLLER_COMMAND:
            event = ZwaveCommandEvent(device=self.device,
                                      state=event.args['state'],
                                      state_description=event.args['state_full'],
                                      error=event.args['error'] if event.args['error_int'] else None,
                                      error_description=event.args['error_full'] if event.args['error_int'] else None,
                                      node=ZwavePlugin.node_to_dict(event.args['node']) if event.args['node'] else None)
        elif event.signal == network.SIGNAL_CONTROLLER_WAITING:
            event = ZwaveCommandWaitingEvent(device=self.device,
                                             state=event.args['state'],
                                             state_description=event.args['state_full'])
        elif event.signal == network.SIGNAL_CREATE_BUTTON:
            event = ZwaveButtonCreatedEvent(device=self.device,
                                            node=ZwavePlugin.node_to_dict(event.args['node']))
        elif event.signal == network.SIGNAL_DELETE_BUTTON:
            event = ZwaveButtonRemovedEvent(device=self.device,
                                            node=ZwavePlugin.node_to_dict(event.args['node']))
        elif event.signal == network.SIGNAL_GROUP:
            event = ZwaveNodeGroupEvent(device=self.device,
                                        node=ZwavePlugin.node_to_dict(event.args['node']),
                                        group_index=event.args['groupidx'])
        elif event.signal == network.SIGNAL_NETWORK_AWAKED:
            event = ZwaveNetworkReadyEvent(
                device=self.device,
                ozw_library_version=self.network.controller.ozw_library_version,
                python_library_version=self.network.controller.python_library_version,
                zwave_library=self.network.controller.library_description,
                home_id=self.network.controller.home_id,
                node_id=self.network.controller.node_id,
                node_version=self.network.controller.node.version,
                nodes_count=self.network.nodes_count,
            )
        elif event.signal == network.SIGNAL_NODE_EVENT:
            event = ZwaveNodeEvent(device=self.device,
                                   node=ZwavePlugin.node_to_dict(event.args['node']))
        elif event.signal == network.SIGNAL_NODE_ADDED:
            event = ZwaveNodeAddedEvent(device=self.device,
                                        node=ZwavePlugin.node_to_dict(event.args['node']))
        elif event.signal == network.SIGNAL_NODE_NAMING:
            event = ZwaveNodeRenamedEvent(device=self.device,
                                          node=ZwavePlugin.node_to_dict(event.args['node']))
        elif event.signal == network.SIGNAL_NODE_READY:
            event = ZwaveNodeReadyEvent(device=self.device,
                                        node=ZwavePlugin.node_to_dict(event.args['node']))
        elif event.signal == network.SIGNAL_NODE_REMOVED:
            event = ZwaveNodeRemovedEvent(device=self.device,
                                          node=ZwavePlugin.node_to_dict(event.args['node']))
        elif event.signal == network.SIGNAL_POLLING_DISABLED:
            event = ZwaveNodePollingEnabledEvent(device=self.device,
                                                 node=ZwavePlugin.node_to_dict(event.args['node']))
        elif event.signal == network.SIGNAL_POLLING_ENABLED:
            event = ZwaveNodePollingDisabledEvent(device=self.device,
                                                  node=ZwavePlugin.node_to_dict(event.args['node']))
        elif event.signal == network.SIGNAL_SCENE_EVENT:
            event = ZwaveNodeSceneEvent(device=self.device,
                                        scene_id=event.args['scene_id'],
                                        node=ZwavePlugin.node_to_dict(event.args['node']))
        elif event.signal == network.SIGNAL_VALUE_ADDED:
            event = ZwaveValueAddedEvent(device=self.device,
                                         node=ZwavePlugin.node_to_dict(event.args['node']),
                                         value=ZwavePlugin.value_to_dict(event.args['value']))
        elif event.signal == network.SIGNAL_VALUE_CHANGED:
            event = ZwaveValueChangedEvent(device=self.device,
                                           node=ZwavePlugin.node_to_dict(event.args['node']),
                                           value=ZwavePlugin.value_to_dict(event.args['value']))
        elif event.signal == network.SIGNAL_VALUE_REFRESHED:
            event = ZwaveValueRefreshedEvent(device=self.device,
                                             node=ZwavePlugin.node_to_dict(event.args['node']),
                                             value=ZwavePlugin.value_to_dict(event.args['value']))
        elif event.signal == network.SIGNAL_VALUE_REMOVED:
            event = ZwaveValueRemovedEvent(device=self.device,
                                           node=ZwavePlugin.node_to_dict(event.args['node']),
                                           value=ZwavePlugin.value_to_dict(event.args['value']))
        else:
            self.logger.info('Received unhandled ZWave event: {}'.format(event))

        if isinstance(event, ZwaveEvent):
            self.bus.post(event)

    def __enter__(self):
        self.start_network()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_network()

    def loop(self):
        try:
            event = event_queue.get(block=True, timeout=1.0)
            self._process_event(event)
        except queue.Empty:
            pass


# vim:sw=4:ts=4:et:
