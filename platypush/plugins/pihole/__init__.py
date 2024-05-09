import hashlib
import requests

from typing import Any, Dict, Optional, Union, List

from platypush.schemas.pihole import PiholeStatusSchema
from platypush.plugins import Plugin, action


class PiholePlugin(Plugin):
    """
    Plugin for interacting with a `Pi-Hole <https://pi-hole.net>`_ DNS server for advertisement and content blocking.
    """

    def __init__(
        self,
        server: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        ssl: bool = False,
        verify_ssl: bool = True,
        timeout: int = 10,
        **kwargs,
    ):
        """
        :param server: Default Pi-hole server IP address.
        :param password: Password for the default Pi-hole server.
        :param api_key: Alternatively to the password, you can also provide the server ``api_key``, as retrieved from
            http://pi-hole-server/admin/scripts/pi-hole/php/api_token.php
        :param ssl: Set to true if the host uses HTTPS (default: False).
        :param verify_ssl: Set to False to disable SSL certificate check.
        :param timeout: Default timeout for the HTTP requests.
        """
        super().__init__(**kwargs)
        self.server = server
        self.password = password
        self.api_key = api_key
        self.ssl = ssl
        self.verify_ssl = verify_ssl
        self.timeout = timeout

    @staticmethod
    def _get_token(
        password: Optional[str] = None, api_key: Optional[str] = None
    ) -> str:
        if not password:
            return api_key or ''
        return hashlib.sha256(
            hashlib.sha256(str(password).encode()).hexdigest().encode()
        ).hexdigest()  # lgtm [py/weak-sensitive-data-hashing]

    def _get_url(
        self,
        name: str,
        server: Optional[str] = None,
        password: Optional[str] = None,
        ssl: Optional[bool] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> str:
        if not server:
            server = self.server
            password = password or self.password
            api_key = api_key or self.api_key
            ssl = ssl if ssl is not None else self.ssl

        args = '&'.join(
            [f'{key}={value}' for key, value in kwargs.items() if value is not None]
        )

        if args:
            args = '&' + args

        token = self._get_token(password=password, api_key=api_key)
        if token:
            token = '&auth=' + token

        return f'http{"s" if ssl else ""}://{server}/admin/api.php?{name}{token}{args}'

    @staticmethod
    def _normalize_number(n: Union[str, int]):
        return int(str(n).replace(',', ''))

    @action
    def status(
        self,
        server: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        ssl: Optional[bool] = None,
    ) -> dict:
        """
        Get the status and statistics of a running Pi-hole server.

        :param server: Server IP address (default: default configured ``server`` value).
        :param password: Server password (default: default configured ``password`` value).
        :param api_key: Server API key (default: default configured ``api_key`` value).
        :param ssl: Set to True if the server uses SSL (default: False).
        :return: .. schema:: pihole.PiholeStatusSchema
        """
        status = requests.get(
            self._get_url(
                'summary', server=server, password=password, api_key=api_key, ssl=ssl
            ),
            verify=self.verify_ssl,
            timeout=self.timeout,
        ).json()

        version = requests.get(
            self._get_url(
                'versions', server=server, password=password, api_key=api_key, ssl=ssl
            ),
            verify=self.verify_ssl,
            timeout=self.timeout,
        ).json()

        return dict(
            PiholeStatusSchema().dump(
                {
                    'server': server or self.server,
                    'status': status.get('status'),
                    'ads_percentage': float(status.get('ads_percentage_today')),
                    'blocked': self._normalize_number(status.get('ads_blocked_today')),
                    'cached': self._normalize_number(status.get('queries_cached')),
                    'domain_count': self._normalize_number(
                        status.get('domains_being_blocked')
                    ),
                    'forwarded': self._normalize_number(
                        status.get('queries_forwarded')
                    ),
                    'queries': self._normalize_number(status.get('dns_queries_today')),
                    'total_clients': self._normalize_number(
                        status.get('clients_ever_seen')
                    ),
                    'total_queries': self._normalize_number(
                        status.get('dns_queries_all_types')
                    ),
                    'unique_clients': self._normalize_number(
                        status.get('unique_clients')
                    ),
                    'unique_domains': self._normalize_number(
                        status.get('unique_domains')
                    ),
                    'version': version.get('core_current'),
                }
            )
        )

    @action
    def enable(
        self,
        server: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        ssl: Optional[bool] = None,
    ):
        """
        Enable a Pi-hole server.

        :param server: Server IP address (default: default configured ``server`` value).
        :param password: Server password (default: default configured ``password`` value).
        :param api_key: Server API key (default: default configured ``api_key`` value).
        :param ssl: Set to True if the server uses SSL (default: False).
        """
        response = requests.get(
            self._get_url(
                'enable', server=server, password=password, api_key=api_key, ssl=ssl
            ),
            verify=self.verify_ssl,
            timeout=self.timeout,
        )

        try:
            status = (response.json() or {}).get('status')
            assert status == 'enabled', 'Wrong credentials'
        except Exception as e:
            raise AssertionError(f'Could not enable the server: {response.text or e}')

        return response.json()

    @action
    def disable(
        self,
        server: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        seconds: Optional[int] = None,
        ssl: Optional[bool] = None,
    ):
        """
        Disable a Pi-hole server.

        :param seconds: How long the server will be disabled in seconds (default: None, indefinitely).
        :param server: Server IP address (default: default configured ``server`` value).
        :param password: Server password (default: default configured ``password`` value).
        :param api_key: Server API key (default: default configured ``api_key`` value).
        :param ssl: Set to True if the server uses SSL (default: False).
        """
        if seconds:
            response = requests.get(
                self._get_url(
                    '',
                    server=server,
                    password=password,
                    api_key=api_key,
                    ssl=ssl,
                    disable=seconds,
                ),
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
        else:
            response = requests.get(
                self._get_url(
                    'disable',
                    server=server,
                    password=password,
                    api_key=api_key,
                    ssl=ssl,
                ),
                verify=self.verify_ssl,
                timeout=self.timeout,
            )

        try:
            status = (response.json() or {}).get('status')
            assert status == 'disabled', 'Wrong credentials'
        except Exception as e:
            raise AssertionError(f'Could not disable the server: {response.text or e}')

        return response.json()

    def _list_manage(
        self,
        domain: str,
        list_name: str,
        endpoint: str,
        server: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        ssl: Optional[bool] = None,
    ):
        data: Dict[str, Any] = {'list': list_name, 'domain': domain}

        if password or self.password:
            data['pw'] = password or self.password
        elif api_key or self.api_key:
            data['auth'] = api_key or self.api_key

        base_url = (
            f"http{'s' if ssl or (ssl is None and self.ssl) else ''}://"
            f"{server or self.server}/admin/scripts/pi-hole/php/{endpoint}.php"
        )

        with requests.session() as s:
            s.get(base_url, verify=self.verify_ssl)
            response = requests.post(
                base_url, data=data, verify=self.verify_ssl, timeout=self.timeout
            ).text.strip()

        return {'response': response}

    def _list_get(
        self, list_name: str, server: Optional[str] = None, ssl: Optional[bool] = None
    ) -> List[str]:
        response = requests.get(
            f"http{'s' if ssl or (ssl is None and self.ssl) else ''}"
            f"://{server or self.server}/admin/scripts/pi-hole/php/"
            f"get.php?list={list_name}",
            verify=self.verify_ssl,
            timeout=10,
        ).json()

        ret = set()
        for ll in response:
            ret.update(ll)
        return list(ret)

    @action
    def get_blacklist(
        self, server: Optional[str] = None, ssl: Optional[bool] = None
    ) -> List[str]:
        """
        Get the content of the blacklist.

        :param server: Server IP address (default: default configured ``server`` value).
        :param ssl: Set to True if the server uses SSL (default: False).
        """
        return self._list_get(list_name='black', server=server, ssl=ssl)

    @action
    def get_whitelist(
        self, server: Optional[str] = None, ssl: Optional[bool] = None
    ) -> List[str]:
        """
        Get the content of the whitelist.

        :param server: Server IP address (default: default configured ``server`` value).
        :param ssl: Set to True if the server uses SSL (default: False).
        """
        return self._list_get(list_name='white', server=server, ssl=ssl)

    @action
    def get_list(
        self, list_name: str, server: Optional[str] = None, ssl: Optional[bool] = None
    ) -> List[str]:
        """
        Get the content of a list stored on the server.

        :param list_name: List name
        :param server: Server IP address (default: default configured ``server`` value).
        :param ssl: Set to True if the server uses SSL (default: False).
        """
        return self._list_get(list_name=list_name, server=server, ssl=ssl)

    @action
    def blacklist_add(
        self,
        domain: str,
        server: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        ssl: Optional[bool] = None,
    ):
        """
        Add a domain to the blacklist.

        :param domain: Domain name.
        :param server: Server IP address (default: default configured ``server`` value).
        :param password: Server password (default: default configured ``password`` value).
        :param api_key: Server API key (default: default configured ``api_key`` value).
        :param ssl: Set to True if the server uses SSL (default: False).
        """
        return self._list_manage(
            domain=domain,
            list_name='black',
            endpoint='add',
            server=server,
            password=password,
            api_key=api_key,
            ssl=ssl,
        )

    @action
    def blacklist_remove(
        self,
        domain: str,
        server: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        ssl: Optional[bool] = None,
    ):
        """
        Remove a domain from the blacklist.

        :param domain: Domain name.
        :param server: Server IP address (default: default configured ``server`` value).
        :param password: Server password (default: default configured ``password`` value).
        :param api_key: Server API key (default: default configured ``api_key`` value).
        :param ssl: Set to True if the server uses SSL (default: False).
        """
        return self._list_manage(
            domain=domain,
            list_name='black',
            endpoint='sub',
            server=server,
            password=password,
            api_key=api_key,
            ssl=ssl,
        )

    @action
    def whitelist_add(
        self,
        domain: str,
        server: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        ssl: Optional[bool] = None,
    ):
        """
        Add a domain to the whitelist.

        :param domain: Domain name.
        :param server: Server IP address (default: default configured ``server`` value).
        :param password: Server password (default: default configured ``password`` value).
        :param api_key: Server API key (default: default configured ``api_key`` value).
        :param ssl: Set to True if the server uses SSL (default: False).
        """
        return self._list_manage(
            domain=domain,
            list_name='white',
            endpoint='add',
            server=server,
            password=password,
            api_key=api_key,
            ssl=ssl,
        )

    @action
    def whitelist_remove(
        self,
        domain: str,
        server: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        ssl: Optional[bool] = None,
    ):
        """
        Remove a domain from the whitelist.

        :param domain: Domain name.
        :param server: Server IP address (default: default configured ``server`` value).
        :param password: Server password (default: default configured ``password`` value).
        :param api_key: Server API key (default: default configured ``api_key`` value).
        :param ssl: Set to True if the server uses SSL (default: False).
        """
        return self._list_manage(
            domain=domain,
            list_name='white',
            endpoint='sub',
            server=server,
            password=password,
            api_key=api_key,
            ssl=ssl,
        )

    @action
    def list_add(
        self,
        list_name: str,
        domain: str,
        server: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        ssl: Optional[bool] = None,
    ):
        """
        Add a domain to a custom list stored on the server.

        :param list_name: List name
        :param domain: Domain name.
        :param server: Server IP address (default: default configured ``server`` value).
        :param password: Server password (default: default configured ``password`` value).
        :param api_key: Server API key (default: default configured ``api_key`` value).
        :param ssl: Set to True if the server uses SSL (default: False).
        """
        return self._list_manage(
            domain=domain,
            list_name=list_name,
            endpoint='add',
            server=server,
            password=password,
            api_key=api_key,
            ssl=ssl,
        )

    @action
    def list_remove(
        self,
        list_name: str,
        domain: str,
        server: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        ssl: Optional[bool] = None,
    ):
        """
        Remove a domain from a custom list stored on the server.

        :param list_name: List name
        :param domain: Domain name.
        :param server: Server IP address (default: default configured ``server`` value).
        :param password: Server password (default: default configured ``password`` value).
        :param api_key: Server API key (default: default configured ``api_key`` value).
        :param ssl: Set to True if the server uses SSL (default: False).
        """
        return self._list_manage(
            domain=domain,
            list_name=list_name,
            endpoint='sub',
            server=server,
            password=password,
            api_key=api_key,
            ssl=ssl,
        )


# vim:sw=4:ts=4:et:
