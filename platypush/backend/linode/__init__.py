from typing import Dict, Optional, List

from platypush.backend.sensor import SensorBackend
from platypush.message.event.linode import LinodeInstanceStatusChanged


class LinodeBackend(SensorBackend):
    """
    This backend monitors the state of one or more Linode instances.

    Triggers:

        * :class:`platypush.message.event.linode.LinodeInstanceStatusChanged` when the status of an instance changes.

    Requires:

        * The :class:`platypush.plugins.linode.LinodePlugin` plugin configured.

    """

    def __init__(self, instances: Optional[List[str]] = None, poll_seconds: float = 30.0, **kwargs):
        """
        :param instances: List of instances to monitor, by label (default: monitor all the instances).
        """
        super().__init__(plugin='linode', poll_seconds=poll_seconds, **kwargs)
        self.instances = set(instances or [])

    def process_data(self, data: Dict[str, dict], *args, **kwargs):
        instances = data['instances']
        old_instances = (self.data or {}).get('instances', {})

        if self.instances:
            instances = {label: instances[label] for label in self.instances if label in instances}

        if not instances:
            return

        for label, instance in instances.items():
            old_instance = old_instances.get(label, {})
            if 'status' in old_instance and old_instance['status'] != instance['status']:
                self.bus.post(LinodeInstanceStatusChanged(instance=label,
                                                          status=instance['status'],
                                                          old_status=old_instance['status']))


# vim:sw=4:ts=4:et:
