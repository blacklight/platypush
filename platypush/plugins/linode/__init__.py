from typing import Collection, List, Optional

from typing_extensions import override

from linode_api4 import LinodeClient, Instance, objects

from platypush.context import get_bus
from platypush.entities.cloud import CloudInstance
from platypush.entities.managers.cloud import CloudInstanceEntityManager, InstanceId
from platypush.entities.managers.switches import EnumSwitchEntityManager
from platypush.entities.switches import EnumSwitch
from platypush.message.event.linode import LinodeInstanceStatusChanged
from platypush.schemas.linode import (
    LinodeInstance,
    LinodeInstanceSchema,
    LinodeInstanceStatus,
)
from platypush.plugins import RunnablePlugin, action


class LinodePlugin(RunnablePlugin, CloudInstanceEntityManager, EnumSwitchEntityManager):
    """
    This plugin can interact with a Linode account and manage node and volumes.

    To get your token:

        - Login to <https://cloud.linode.com/>.
        - Go to My Profile -> API Tokens -> Add a Personal Access Token.
        - Select the scopes that you want to provide to your new token.

    Requires:

        * **linode_api4** (``pip install linode_api4``)

    Triggers:

        * :class:`platypush.message.event.linode.LinodeInstanceStatusChanged` when the status of an instance changes.

    """

    def __init__(self, token: str, poll_interval: float = 60.0, **kwargs):
        """
        :param token: Linode API token.
        :param poll_interval: How often to poll the Linode API
            (default: 60 seconds).
        """
        super().__init__(poll_interval=poll_interval, **kwargs)
        self._token = token

    def _get_client(self, token: Optional[str] = None) -> LinodeClient:
        """
        Get a :class:`LinodeClient` instance.

        :param token: Override the default token.
        """
        return LinodeClient(token or self._token)

    def _get_instance(
        self, instance: InstanceId, token: Optional[str] = None
    ) -> Instance:
        """
        Get an instance by name or ID.

        :param instance: The label, ID or host UUID of the instance.
        :param token: Override the default token.
        """
        client = self._get_client(token)
        if isinstance(instance, str):
            filters = [Instance.label == instance]
        elif isinstance(instance, int):
            filters = [Instance.id == instance]
        else:
            raise AssertionError(f'Invalid instance type: {type(instance)}')

        instances = client.linode.instances(*filters)
        assert instances, f'No such Linode instance: {instance}'
        return instances[0]

    def _linode_instance_to_dict(self, instance: Instance) -> dict:
        """
        Convert an internal :class:`linode_api4.Instance` to a
        dictionary representation that can be used to create a
        :class:`platypush.entities.cloud.CloudInstance` object.
        """
        return {
            key: (value.dict if isinstance(value, objects.MappedObject) else value)
            for key, value in instance.__dict__.items()
            if not key.startswith('_')
        }

    @override
    def main(self):
        instances = []

        while not self.should_stop():
            status = {instance.id: instance for instance in instances}

            new_status = {
                instance.id: instance
                for instance in self.status(publish_entities=False).output
            }

            changed_instances = (
                [
                    instance
                    for instance in new_status.values()
                    if not (
                        status.get(instance.id)
                        and status[instance.id].status == instance.status
                    )
                ]
                if new_status
                else []
            )

            if changed_instances:
                for instance in changed_instances:
                    get_bus().post(
                        LinodeInstanceStatusChanged(
                            instance_id=instance.id,
                            instance_name=instance.name,
                            status=instance.status,
                            old_status=(
                                status[instance.id].status
                                if status.get(instance.id)
                                else None
                            ),
                        )
                    )

                self.publish_entities(changed_instances)

            instances = new_status.values()
            self.wait_stop(self.poll_interval)

    @override
    def transform_entities(
        self, entities: Collection[LinodeInstance]
    ) -> Collection[CloudInstance]:
        schema = LinodeInstanceSchema()
        return super().transform_entities(
            [
                CloudInstance(
                    reachable=instance.status == LinodeInstanceStatus.RUNNING,
                    children=[
                        EnumSwitch(
                            id=f'{instance.id}:__action__',
                            name='Actions',
                            values=['boot', 'reboot', 'shutdown'],
                            is_write_only=True,
                        )
                    ],
                    **schema.dump(instance),
                )
                for instance in entities
            ]
        )

    @action
    @override
    def status(
        self,
        *_,
        instance: Optional[InstanceId] = None,
        token: Optional[str] = None,
        publish_entities: bool = True,
        **__,
    ) -> List[LinodeInstance]:
        """
        Get the full status and info of the instances associated to a selected account.

        :param token: Override the default access token if you want to query another account.
        :param instance: Select only one instance, either by name, ID or host UUID.
        :param publish_entities: Whether
            :class:`platypush.message.event.entities.EntityUpdateEvent` should
            be published for all the instances, whether or not their status has
            changed (default: ``True``).
        :return: .. schema:: linode.LinodeInstanceSchema(many=True)
        """
        instances = (
            [self._get_instance(instance=instance)]
            if instance
            else [
                instance
                for page in self._get_client(token).linode.instances().lists
                for instance in page
            ]
        )

        mapped_instances = LinodeInstanceSchema(many=True).load(
            map(self._linode_instance_to_dict, instances)
        )

        if publish_entities:
            self.publish_entities(mapped_instances)

        return mapped_instances

    @override
    @action
    def reboot(self, instance: InstanceId, token: Optional[str] = None, **_):
        """
        Reboot an instance.

        :param instance: Instance ID, label or host UUID.
        :param token: Default access token override.
        """
        node = self._get_instance(instance=instance, token=token)
        assert node.reboot(), 'Reboot failed'

    @override
    @action
    def boot(self, instance: InstanceId, token: Optional[str] = None, **_):
        """
        Boot an instance.

        :param instance: Instance ID, label or host UUID.
        :param token: Default access token override.
        """
        node = self._get_instance(instance=instance, token=token)
        assert node.boot(), 'Boot failed'

    @override
    @action
    def shutdown(self, instance: InstanceId, token: Optional[str] = None, **_):
        """
        Shutdown an instance.

        :param instance: Instance ID, label or host UUID.
        :param token: Default access token override.
        """
        node = self._get_instance(instance=instance, token=token)
        assert node.shutdown(), 'Shutdown failed'

    @override
    @action
    def set(self, entity: str, value: str, **kwargs):
        """
        Entity framework compatible method to run an action on the instance
        through an ``EnumSwitch``.

        :param entity: Entity ID, as ``<instance_id>`` or
            ``<instance_id>:__action__``.
        :param value: Action to run, one among ``boot``, ``reboot`` and
            ``shutdown``.
        """
        try:
            instance_id = int(entity.removesuffix(':__action__'))
        except (TypeError, ValueError) as e:
            raise AssertionError(f'Invalid entity: {entity}') from e

        assert value in {'boot', 'reboot', 'shutdown'}, f'Invalid action: {value}'
        method = getattr(self, value)
        return method(instance_id, **kwargs)


# vim:sw=4:ts=4:et:
