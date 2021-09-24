import os
from typing import Optional, Union, Callable

from platypush.context import get_bus
from platypush.message.event.ngrok import NgrokProcessStartedEvent, NgrokTunnelStartedEvent, NgrokTunnelStoppedEvent, \
    NgrokProcessStoppedEvent
from platypush.plugins import Plugin, action
from platypush.schemas.ngrok import NgrokTunnelSchema


class NgrokPlugin(Plugin):
    """
    Plugin to dynamically create and manage network tunnels using `ngrok <https://ngrok.com/>`_.

    Requires:

        * **pyngrok** (``pip install pyngrok``)

    Triggers:

        * :class:`platypush.message.event.ngrok.NgrokProcessStartedEvent` when the ``ngrok`` process is started.
        * :class:`platypush.message.event.ngrok.NgrokProcessStoppedEvent` when the ``ngrok`` process is stopped.
        * :class:`platypush.message.event.ngrok.NgrokTunnelStartedEvent` when a tunnel is started.
        * :class:`platypush.message.event.ngrok.NgrokTunnelStoppedEvent` when a tunnel is stopped.

    """

    def __init__(self, auth_token: Optional[str] = None, ngrok_bin: Optional[str] = None, region: Optional[str] = None,
                 **kwargs):
        """
        :param auth_token: Specify the ``ngrok`` auth token, enabling authenticated features (e.g. more concurrent
            tunnels, custom subdomains, etc.).
        :param ngrok_bin: By default ``pyngrok`` manages its own version of the ``ngrok`` binary, but you can specify
            this option if you want to use a different binary installed on the system.
        :param region: ISO code of the region/country that should host the ``ngrok`` tunnel (default: ``us``).
        """
        from pyngrok import conf, ngrok
        super().__init__(**kwargs)

        conf.get_default().log_event_callback = self._get_event_callback()
        self._active_tunnels_by_url = {}

        if auth_token:
            ngrok.set_auth_token(auth_token)
        if ngrok_bin:
            conf.get_default().ngrok_path = os.path.expanduser(ngrok_bin)
        if region:
            conf.get_default().region = region

    @property
    def _active_tunnels_by_name(self) -> dict:
        return {
            tunnel['name']: tunnel
            for tunnel in self._active_tunnels_by_url.values()
        }

    def _get_event_callback(self) -> Callable:
        from pyngrok.process import NgrokLog

        def callback(log: NgrokLog):
            if log.msg == 'client session established':
                get_bus().post(NgrokProcessStartedEvent())
            elif log.msg == 'started tunnel':
                # noinspection PyUnresolvedReferences
                tunnel = dict(
                    name=log.name,
                    url=log.url,
                    protocol=log.url.split(':')[0]
                )

                self._active_tunnels_by_url[tunnel['url']] = tunnel
                get_bus().post(NgrokTunnelStartedEvent(**tunnel))
            elif (
                    log.msg == 'end' and
                    int(getattr(log, 'status', 0)) == 204 and
                    getattr(log, 'pg', '').startswith('/api/tunnels')
            ):
                # noinspection PyUnresolvedReferences
                tunnel = log.pg.split('/')[-1]
                tunnel = self._active_tunnels_by_name.pop(tunnel, self._active_tunnels_by_url.pop(tunnel, None))
                if tunnel:
                    get_bus().post(NgrokTunnelStoppedEvent(**tunnel))
            elif log.msg == 'received stop request':
                get_bus().post(NgrokProcessStoppedEvent())

        return callback

    @action
    def create_tunnel(self, resource: Union[int, str] = 80, protocol: str = 'tcp',
                      name: Optional[str] = None, auth: Optional[str] = None, **kwargs) -> dict:
        """
        Create an ``ngrok`` tunnel to the specified localhost port/protocol.

        :param resource: This can be any of the following:

            - A TCP or UDP port exposed on localhost.
            - A local network address (or ``address:port``) to expose.
            - The absolute path (starting with ``file://``) to a local folder - in such case, the specified directory
              will be served over HTTP through an ``ngrok`` endpoint (see https://ngrok.com/docs#http-file-urls).

            Default: localhost port 80.

        :param protocol: Network protocol (default: ``tcp``).
        :param name: Optional tunnel name.
        :param auth: HTTP basic authentication credentials associated with the tunnel, in the format of
            ``username:password``.
        :param kwargs: Extra arguments supported by the ``ngrok`` tunnel, such as ``hostname``, ``subdomain`` or
            ``remote_addr`` - see the `ngrok documentation <https://ngrok.com/docs#tunnel-definitions>`_ for a full
            list.
        :return: .. schema:: ngrok.NgrokTunnelSchema
        """
        from pyngrok import ngrok
        if isinstance(resource, str) and resource.startswith('file://'):
            protocol = None

        tunnel = ngrok.connect(resource, proto=protocol, name=name, auth=auth, **kwargs)
        return NgrokTunnelSchema().dump(tunnel)

    @action
    def close_tunnel(self, tunnel: str):
        """
        Close an ``ngrok`` tunnel.

        :param tunnel: Name or public URL of the tunnel to be closed.
        """
        from pyngrok import ngrok

        if tunnel in self._active_tunnels_by_name:
            tunnel = self._active_tunnels_by_name[tunnel]['url']

        assert tunnel in self._active_tunnels_by_url, f'No such tunnel URL or name: {tunnel}'
        ngrok.disconnect(tunnel)

    @action
    def get_tunnels(self):
        """
        Get the list of active ``ngrok`` tunnels.

        :return: .. schema:: ngrok.NgrokTunnelSchema(many=True)
        """
        from pyngrok import ngrok
        tunnels = ngrok.get_tunnels()
        return NgrokTunnelSchema().dump(tunnels, many=True)

    @action
    def kill_process(self):
        """
        The first created tunnel instance also starts the ``ngrok`` process.
        The process will stay alive until the Python interpreter is stopped or this action is invoked.
        """
        from pyngrok import ngrok
        proc = ngrok.get_ngrok_process()
        assert proc and proc.proc, 'The ngrok process is not running'
        proc.proc.kill()
        get_bus().post(NgrokProcessStoppedEvent())


# vim:sw=4:ts=4:et:
