from typing import Optional, Union

from linode_api4 import LinodeClient, Instance
from platypush.plugins.sensor import SensorPlugin

from platypush.message.response.linode import LinodeInstancesResponse, LinodeInstanceResponse
from platypush.plugins import action


class LinodePlugin(SensorPlugin):
    """
    This plugin can interact with a Linode account and manage node and volumes.

    To get your token:

        - Login to <https://cloud.linode.com/>.
        - Go to My Profile -> API Tokens -> Add a Personal Access Token.
        - Select the scopes that you want to provide to your new token.

    Requires:

        * **linode_api4** (``pip install linode_api4``)

    """

    def __init__(self, token: str, **kwargs):
        """
        :param token: Your Linode token.
        """

        super().__init__(**kwargs)
        self._token = token

    def _get_client(self, token: Optional[str] = None) -> LinodeClient:
        return LinodeClient(token or self._token)

    def _get_instance(self, label: str, token: Optional[str] = None) -> Instance:
        client = self._get_client(token)
        instances = client.linode.instances(Instance.label == label)
        assert instances, 'No such Linode instance: ' + label
        return instances[0]

    @action
    def status(self, token: Optional[str] = None, instance: Optional[str] = None) \
            -> Union[LinodeInstanceResponse, LinodeInstancesResponse]:
        """
        Get the full status and info of the instances associated to a selected account.

        :param token: Override the default access token if you want to query another account.
        :param instance: Select only one node by label.
        :return: :class:`platypush.message.response.linode.LinodeInstanceResponse` if ``label`` is specified,
            :class:`platypush.message.response.linode.LinodeInstancesResponse` otherwise.
        """
        if instance:
            instance = self._get_instance(label=instance)
            return LinodeInstanceResponse(instance=instance)

        client = self._get_client(token)
        return LinodeInstancesResponse(instances=client.linode.instances())

    @action
    def reboot(self, instance: str, token: Optional[str] = None) -> None:
        """
        Reboot an instance.

        :param instance: Label of the instance to be rebooted.
        :param token: Default access token override.
        """
        instance = self._get_instance(label=instance, token=token)
        assert instance.reboot(), 'Reboot failed'

    @action
    def boot(self, instance: str, token: Optional[str] = None) -> None:
        """
        Boot an instance.

        :param instance: Label of the instance to be booted.
        :param token: Default access token override.
        """
        instance = self._get_instance(label=instance, token=token)
        assert instance.boot(), 'Boot failed'

    @action
    def shutdown(self, instance: str, token: Optional[str] = None) -> None:
        """
        Shutdown an instance.

        :param instance: Label of the instance to be shut down.
        :param token: Default access token override.
        """
        instance = self._get_instance(label=instance, token=token)
        assert instance.shutdown(), 'Shutdown failed'

    @action
    def get_measurement(self, *args, **kwargs):
        return self.status(*args, **kwargs)


# vim:sw=4:ts=4:et:
