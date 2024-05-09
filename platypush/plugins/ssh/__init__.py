import base64
import datetime
import errno
import getpass
import os
import threading

from binascii import hexlify
from stat import (
    S_ISDIR,
    S_ISREG,
    S_ISLNK,
    S_ISCHR,
    S_ISFIFO,
    S_ISSOCK,
    S_ISBLK,
    S_ISDOOR,
)
from typing import Optional, Dict, Tuple, List, Union, Any

from paramiko import DSSKey, RSAKey, SSHClient, WarningPolicy, SFTPClient

try:
    from paramiko.util import u
except ImportError:
    from paramiko.py3compat import u  # type: ignore

try:
    from paramiko import GSS_AUTH_AVAILABLE  # type: ignore
except ImportError:
    from paramiko.ssh_gss import GSS_AUTH_AVAILABLE

from platypush import Response
from platypush.plugins import Plugin, action
from platypush.plugins.ssh.tunnel.forward import forward_tunnel
from platypush.plugins.ssh.tunnel.reverse import reverse_tunnel, close_tunnel


class SshPlugin(Plugin):
    """
    SSH plugin.
    """

    key_dispatch_table = {'dsa': DSSKey, 'rsa': RSAKey}

    def __init__(
        self, key_file: Optional[str] = None, passphrase: Optional[str] = None, **kwargs
    ):
        """
        :param key_file: Default key file (default: any "id_rsa", "id_dsa",
            "id_ecdsa", or "id_ed25519" key discoverable in ``~/.ssh/``.
        :param passphrase: Key file passphrase (default: None).
        """
        super().__init__(**kwargs)
        self.key_file = (
            os.path.abspath(os.path.expanduser(key_file)) if key_file else None
        )
        self.passphrase = passphrase
        self._sessions: Dict[Tuple[str, int, Optional[str]], SSHClient] = {}
        self._fwd_tunnels: Dict[Tuple[int, str, int], dict] = {}
        self._rev_tunnels: Dict[Tuple[int, str, int], dict] = {}

    def _get_key(
        self, key_file: Optional[str] = None, passphrase: Optional[str] = None
    ):
        key_file = key_file or self.key_file
        return (
            os.path.abspath(os.path.expanduser(key_file)) if key_file else None,
            passphrase or self.passphrase,
        )

    @staticmethod
    def _get_host_port_user(host: str, port: int = 22, user: Optional[str] = None, **_):
        if host.find('@') >= 0:
            user, host = host.split('@')
        if host.find(':') >= 0:
            host, p = host.split(':')
            port = int(p)
        if not user:
            user = getpass.getuser()

        return host, port, user

    @action
    def keygen(
        self,
        filename: str,
        type: str = 'rsa',  # pylint: disable=redefined-builtin
        bits: int = 4096,
        comment: Optional[str] = None,
        passphrase: Optional[str] = None,
    ) -> dict:
        """
        Generate an SSH keypair.

        :param filename: Output file name for the private key (the public key
            will be stored in <filename>.pub).
        :param type: Encryption algorithm, either "rsa" or "dsa" (default: "rsa").
        :param bits: Key length in bits (default: 4096).
        :param comment: Key comment (default: None).
        :param passphrase: Key passphrase (default: None).
        :return:

            .. code-block:: json

              {
                "fingerprint": "SHA256:...",
                "key_file": "private_key_file",
                "pub_key_file": "public_key_file"
              }

        """
        assert type != 'dsa' or bits <= 1024, 'DSA keys support a maximum of 1024 bits'
        assert (
            type in self.key_dispatch_table
        ), f'No such type: {type}. Available types: {self.key_dispatch_table.keys()}'

        if filename:
            filename = os.path.abspath(os.path.expanduser(filename))

        prv = self.key_dispatch_table[type].generate(bits=bits)
        prv.write_private_key_file(filename=filename, password=passphrase)
        pub = self.key_dispatch_table[type](filename=filename, password=passphrase)
        pub_file = f'{filename}.pub'
        with open(pub_file, 'w') as f:
            f.write(f'{pub.get_name()} {pub.get_base64()}')
            if comment:
                f.write(' ' + comment)

        return {
            'fingerprint': u(hexlify(pub.get_fingerprint())),
            'key_file': filename,
            'pub_key_file': pub_file,
        }

    def run(self, *args, **kwargs):
        try:
            return super().run(*args, **kwargs)
        except Exception as e:
            raise AssertionError(e) from e

    def _connect(
        self,
        host: str,
        port: int = 22,
        user: Optional[str] = None,
        password: Optional[str] = None,
        key_file: Optional[str] = None,
        passphrase: Optional[str] = None,
        compress: bool = False,
        timeout: Optional[int] = None,
        auth_timeout: Optional[int] = None,
    ) -> SSHClient:
        try:
            host, port, user = self._get_host_port_user(host, port, user)
            key = (host, port, user)
            if key in self._sessions:
                self.logger.info(
                    '[Connect] The SSH session is already active: %s@%s:%d',
                    user,
                    host,
                    port,
                )
                return self._sessions[key]

            key_file, passphrase = self._get_key(key_file, passphrase)
            client = SSHClient()
            client.set_missing_host_key_policy(WarningPolicy())

            args = {
                'hostname': host,
                'port': port,
                'username': user,
                'compress': compress,
                'timeout': timeout,
                'auth_timeout': auth_timeout,
            }

            if password:
                args['password'] = password
            elif key_file:
                args['key_filename'] = key_file
                args['passphrase'] = passphrase
                args['gss_auth'] = GSS_AUTH_AVAILABLE
                args['gss_kex'] = GSS_AUTH_AVAILABLE
            else:
                client.load_system_host_keys()

            client.connect(**args)
            self._sessions[key] = client
            return client
        except Exception as e:
            self.logger.exception(e)
            raise AssertionError(f'Connection to {host} failed: {type(e)}: {e}')

    @action
    def connect(
        self,
        host: str,
        port: int = 22,
        user: Optional[str] = None,
        password: Optional[str] = None,
        key_file: Optional[str] = None,
        passphrase: Optional[str] = None,
        compress: bool = False,
        timeout: Optional[int] = None,
        auth_timeout: Optional[int] = None,
    ) -> None:
        """
        Open an SSH connection.

        :param host: Host name or IP. Can also be in the format ``[user]@<host>:[port]``.
        :param port: Remote port (default: 22).
        :param user: Username (default: None, same user name as the one running platypush).
        :param password: Password (default: None).
        :param key_file: Key file to use for authentication (default: None).
        :param passphrase: Passphrase for the key file (default: None).
        :param compress: Compress data on the connection (default: False).
        :param timeout: Data transfer timeout in seconds (default: None).
        :param auth_timeout: Authentication timeout in seconds (default: None).
        """
        self._connect(
            host=host,
            port=port,
            user=user,
            password=password,
            key_file=key_file,
            passphrase=passphrase,
            compress=compress,
            timeout=timeout,
            auth_timeout=auth_timeout,
        )

    @action
    def disconnect(self, host: str, port: int = 22, user: Optional[str] = None) -> None:
        """
        Close a connection to a host.

        :param host: Host name or IP. Can also be in the format ``[user]@<host>:[port]``.
        :param port: Remote port (default: 22).
        :param user: Username (default: None, same user name as the one running platypush).
        """
        host, port, user = self._get_host_port_user(host, port, user)
        key = (host, port, user)
        if key not in self._sessions:
            self.logger.info(
                '[Disconnect] The SSH session is not active: %s@%s:%d', user, host, port
            )

        session = self._sessions[key]
        try:
            session.close()
        except Exception as e:
            self.logger.exception(e)

        del self._sessions[key]

    @action
    def exec(
        self,
        cmd: str,
        keep_alive: bool = False,
        timeout: Optional[int] = None,
        stdin: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Response:
        """
        Run a command on a host.

        :param cmd: Command to run
        :param keep_alive: Keep the connection active after running the command (default: False).
        :param timeout: Communication timeout in seconds (default: None).
        :param stdin: Optional string to pass on the stdin of the command.
        :param env: Dictionary of environment variables to be used for the connection (default: None).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        :return: The output of the executed command.
        """
        client = self._connect(**kwargs)

        def decode(buf: bytes) -> str:
            try:
                s_buf = buf.decode()
            except (ValueError, TypeError):
                s_buf = base64.encodebytes(buf).decode()

            if s_buf.endswith('\n'):
                s_buf = s_buf[:-1]
            return s_buf

        try:
            _in, _out, _err = client.exec_command(cmd, timeout=timeout, environment=env)
            if stdin:
                with _in:
                    _in.write(stdin)

            resp = Response()
            with _out:
                resp.output = decode(_out.read())
            with _err:
                err = decode(_err.read())
                if err:
                    resp.errors = [err]

            return resp
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @staticmethod
    def is_directory(sftp: SFTPClient, path: str) -> bool:
        f = sftp.lstat(path)
        if f.st_mode is None:
            return False

        return S_ISDIR(f.st_mode)

    @classmethod
    def sftp_walk(cls, sftp: SFTPClient, path: str):
        files = []
        folders = []

        for f in sftp.listdir_attr(path):
            if f.st_mode is not None and S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)

        yield path, folders, files

        for folder in folders:
            new_path = os.path.join(path, folder)
            yield from cls.sftp_walk(sftp, new_path)

    def sftp_get(
        self,
        sftp: SFTPClient,
        remote_path: str,
        local_path: str,
        recursive: bool = False,
    ) -> None:
        if self.is_directory(sftp, remote_path):
            assert (
                recursive
            ), '{} is a directory on the server but recursive has been set to False'
            local_path = os.path.join(local_path, os.path.basename(remote_path))
            os.makedirs(local_path, mode=0o755, exist_ok=True)
            sftp.chdir(remote_path)

            for path, _, files in self.sftp_walk(sftp, '.'):
                new_local_path = os.path.join(local_path, path)
                os.makedirs(new_local_path, mode=0o755, exist_ok=True)

                for file in files:
                    self.logger.info(
                        'Downloading file %s from %s to %s', file, path, new_local_path
                    )

                    self.sftp_get(
                        sftp,
                        os.path.join(remote_path, path, file),
                        os.path.join(new_local_path, file),
                        recursive=recursive,
                    )
        else:
            if os.path.isdir(local_path):
                local_path = os.path.join(local_path, os.path.basename(remote_path))

            sftp.get(remote_path, local_path)

    @action
    def get(
        self,
        remote_path: str,
        local_path: str,
        recursive: bool = False,
        keep_alive: bool = False,
        **kwargs,
    ) -> None:
        """
        Download a file or folder from an SSH server.

        :param remote_path: Remote path (file or directory).
        :param local_path: Local path (file or directory).
        :param recursive: Set to True if you want to recursively download folders (default: False).
        :param keep_alive: Keep the connection active after running the command (default: False).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        local_path = os.path.abspath(os.path.expanduser(local_path))
        kwargs['compress'] = True
        client = self._connect(**kwargs)
        sftp = client.open_sftp()

        try:
            self.sftp_get(
                sftp,
                remote_path=remote_path,
                local_path=local_path,
                recursive=recursive,
            )
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @action
    def put(
        self,
        remote_path: str,
        local_path: str,
        recursive: bool = False,
        keep_alive: bool = False,
        **kwargs,
    ) -> None:
        """
        Upload a file or folder to an SSH server.

        :param remote_path: Remote path (file or directory).
        :param local_path: Local path (file or directory).
        :param recursive: Set to True if you want to recursively upload folders (default: False).
        :param keep_alive: Keep the connection active after running the command (default: False).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        local_path = os.path.abspath(os.path.expanduser(local_path))
        assert os.path.exists(local_path), os.strerror(errno.ENOENT)
        kwargs['compress'] = True
        client = self._connect(**kwargs)
        sftp = client.open_sftp()

        try:
            if os.path.isdir(local_path):
                try:
                    sftp.mkdir(remote_path)
                except Exception as e:
                    self.logger.warning(
                        'mkdir %s failed: %s: %s', remote_path, type(e), e
                    )

                assert (
                    recursive
                ), f'{local_path} is a directory but recursive has been set to False'

                assert self.is_directory(
                    sftp, remote_path
                ), f'{remote_path} is not a directory on the remote host'

                sftp.chdir(remote_path)
                os.chdir(local_path)

                for path, _, files in os.walk('.'):
                    try:
                        sftp.mkdir(path)
                    except Exception as e:
                        self.logger.warning(
                            'mkdir %s failed: %s: %s', remote_path, type(e), e
                        )

                    for file in files:
                        src = os.path.join(path, file)
                        dst = os.path.join(path, file)
                        self.logger.info('Copying %s to %s', src, dst)
                        sftp.put(src, dst)
            else:
                if self.is_directory(sftp, remote_path):
                    remote_path = os.path.join(
                        remote_path, os.path.basename(local_path)
                    )

                sftp.put(local_path, remote_path)
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @action
    def ls(
        self, path: str = '.', attrs: bool = False, keep_alive: bool = False, **kwargs
    ) -> Union[List[str], Dict[str, Any]]:
        """
        Return the list of files in a path on a remote server.

        :param path: Remote path (default: current directory).
        :param keep_alive: Keep the connection active after running the command (default: False).
        :param attrs: Set to True if you want to get the full information of each file (default: False).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        :return: A list of filenames if ``attrs=False``, otherwise a dictionary ``filename -> {attributes`` if
            ``attrs=True``.
        """
        client = self._connect(**kwargs)
        sftp = client.open_sftp()

        def get_file_type(st_mode: Optional[int]) -> str:
            if st_mode is None:
                return 'unknown'
            if S_ISDIR(st_mode):
                return 'directory'
            elif S_ISBLK(st_mode):
                return 'block'
            elif S_ISCHR(st_mode):
                return 'device'
            elif S_ISDOOR(st_mode):
                return 'door'
            elif S_ISREG(st_mode):
                return 'file'
            elif S_ISLNK(st_mode):
                return 'link'
            elif S_ISFIFO(st_mode):
                return 'fifo'
            elif S_ISSOCK(st_mode):
                return 'sock'
            else:
                return 'unknown'

        try:
            if attrs:
                return {
                    f.filename: {
                        'filename': f.filename,
                        'longname': f.longname,
                        'attributes': f.attr,
                        'type': get_file_type(f.st_mode),
                        'access_time': (
                            datetime.datetime.fromtimestamp(f.st_atime)
                            if f.st_atime
                            else None
                        ),
                        'modify_time': (
                            datetime.datetime.fromtimestamp(f.st_mtime)
                            if f.st_mtime
                            else None
                        ),
                        'uid': f.st_uid,
                        'gid': f.st_gid,
                        'size': f.st_size,
                    }
                    for f in sftp.listdir_attr(path)
                }

            return sftp.listdir(path)
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @action
    def rm(self, path: str, keep_alive: bool = False, **kwargs) -> None:
        """
        Remove a file from the server.

        :param path: Remote path to remove.
        :param keep_alive: Keep the connection active after running the command (default: False).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        client = self._connect(**kwargs)
        sftp = client.open_sftp()

        try:
            sftp.remove(path)
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @action
    def mv(self, path: str, new_path: str, keep_alive: bool = False, **kwargs) -> None:
        """
        Move/rename a file.

        :param path: Remote path to move/rename.
        :param new_path: Destination path.
        :param keep_alive: Keep the connection active after running the command (default: False).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        client = self._connect(**kwargs)
        sftp = client.open_sftp()

        try:
            sftp.posix_rename(path, new_path)
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @action
    def mkdir(
        self, path: str, mode: int = 0o777, keep_alive: bool = False, **kwargs
    ) -> None:
        """
        Create a directory.

        :param path: Path to be created.
        :param mode: Access permissions (default: 0777).
        :param keep_alive: Keep the connection active after running the command (default: False).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        client = self._connect(**kwargs)
        sftp = client.open_sftp()

        try:
            sftp.mkdir(path, mode=mode)
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @action
    def rmdir(self, path: str, keep_alive: bool = False, **kwargs) -> None:
        """
        Remove a directory.

        :param path: Path to be removed.
        :param keep_alive: Keep the connection active after running the command (default: False).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        client = self._connect(**kwargs)
        sftp = client.open_sftp()

        try:
            sftp.rmdir(path)
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @action
    def ln(self, src: str, dest: str, keep_alive: bool = False, **kwargs) -> None:
        """
        Create a symbolic link.

        :param src: Source path.
        :param dest: Destination path.
        :param keep_alive: Keep the connection active after running the command (default: False).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        client = self._connect(**kwargs)
        sftp = client.open_sftp()

        try:
            sftp.symlink(src, dest)
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @action
    def chmod(self, path: str, mode: int, keep_alive: bool = False, **kwargs) -> None:
        """
        Change the access rights of a path.

        :param path: Path to be modified.
        :param mode: Access permissions (in octal mode).
        :param keep_alive: Keep the connection active after running the command (default: False).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        client = self._connect(**kwargs)
        sftp = client.open_sftp()

        try:
            sftp.chmod(path, mode=mode)
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @action
    def chown(
        self, path: str, uid: int, gid: int, keep_alive: bool = False, **kwargs
    ) -> None:
        """
        Change the owner of a path.

        :param path: Path to be modified.
        :param uid: New user ID.
        :param gid: New group ID.
        :param keep_alive: Keep the connection active after running the command (default: False).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        client = self._connect(**kwargs)
        sftp = client.open_sftp()

        try:
            sftp.chown(path, uid=uid, gid=gid)
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @action
    def chdir(self, path: str, keep_alive: bool = False, **kwargs) -> None:
        """
        Change directory to the specified path.

        :param path: Destination path.
        :param keep_alive: Keep the connection active after running the command (default: False).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        client = self._connect(**kwargs)
        sftp = client.open_sftp()

        try:
            sftp.chdir(path)
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @action
    def getcwd(self, keep_alive: bool = False, **kwargs) -> str:
        """
        Get the current working directory.

        :param keep_alive: Keep the connection active after running the command (default: False).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        client = self._connect(**kwargs)
        sftp = client.open_sftp()

        try:
            return sftp.getcwd() or '/'
        finally:
            if not keep_alive:
                host, port, user = self._get_host_port_user(**kwargs)
                self.disconnect(host=host, port=port, user=user)

    @action
    def start_forward_tunnel(
        self,
        local_port: int,
        remote_host: str,
        remote_port: int,
        bind_addr: str = '',
        **kwargs,
    ):
        """
        Start an SSH forward tunnel, tunnelling ``<local_port>`` to
        ``<remote_host>:<remote_port>``.

        :param local_port: Local port.
        :param remote_host: Remote host.
        :param remote_port: Remote port.
        :param bind_addr: If set, the `local_port` will be bound to this
            address/subnet (default: '', or 0.0.0.0: any).
        :param kwargs: Arguments for
            :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        key = local_port, remote_host, remote_port
        if key in self._fwd_tunnels:
            self.logger.info(
                'The tunnel %s:%d:%s:%d is already active',
                bind_addr,
                local_port,
                remote_host,
                remote_port,
            )
            return

        client = self._connect(**kwargs)
        server = forward_tunnel(
            local_port,
            remote_host,
            remote_port,
            client.get_transport(),
            bind_addr=bind_addr,
        )
        threading.Thread(target=server.serve_forever, name='sshfwdtun').start()

        self._fwd_tunnels[key] = {
            'client': client,
            'server': server,
            'args': kwargs,
        }

    @action
    def stop_forward_tunnel(self, local_port: int, remote_host: str, remote_port: int):
        """
        Stop an active SSH forward tunnel.

        :param local_port: Local port.
        :param remote_host: Remote host.
        :param remote_port: Remote port.
        """
        key = (local_port, remote_host, remote_port)
        if key not in self._fwd_tunnels:
            self.logger.warning(
                'No such forward tunnel: %d:%s:%d', local_port, remote_host, remote_port
            )
            return

        server = self._fwd_tunnels[key]['server']
        server.server_close()

        args = self._fwd_tunnels[key]['args']
        host, port, user = self._get_host_port_user(**args)
        self.disconnect(host=host, port=port, user=user)

    @action
    def start_reverse_tunnel(
        self,
        server_port: int,
        remote_host: str,
        remote_port: int,
        bind_addr: str = '',
        **kwargs,
    ):
        """
        Start an SSH reversed tunnel. <server_port> on the SSH server is forwarded across an SSH session back to the
        local machine, and out to a <remote_host>:<remote_port> reachable from this network.

        :param server_port: Server port.
        :param remote_host: Remote host.
        :param remote_port: Remote port.
        :param bind_addr: If set, the `server_port` will be bound to this address/subnet (default: '', or 0.0.0.0: any).
        :param kwargs: Arguments for :meth:`platypush.plugins.ssh.SshPlugin.connect`.
        """
        key = server_port, remote_host, remote_port
        if key in self._fwd_tunnels:
            self.logger.info(
                'The tunnel %s:%d:%s:%d is already active',
                bind_addr,
                server_port,
                remote_host,
                remote_port,
            )
            return

        client = self._connect(**kwargs)
        server = reverse_tunnel(
            server_port,
            remote_host,
            remote_port,
            transport=client.get_transport(),
            bind_addr=bind_addr,
        )

        threading.Thread(target=server, name='sshrevtun').start()

        self._rev_tunnels[key] = {
            'client': client,
            'server': server,
            'args': kwargs,
        }

    @action
    def stop_reverse_tunnel(self, server_port: int, remote_host: str, remote_port: int):
        """
        Stop an active SSH reversed tunnel.

        :param server_port: Server port.
        :param remote_host: Remote host.
        :param remote_port: Remote port.
        """
        key = (server_port, remote_host, remote_port)
        if key not in self._rev_tunnels:
            self.logger.warning(
                'No such reverse tunnel: %d:%s:%d',
                server_port,
                remote_host,
                remote_port,
            )
            return

        close_tunnel(*key)
        args = self._rev_tunnels[key]['args']
        host, port, user = self._get_host_port_user(**args)
        self.disconnect(host=host, port=port, user=user)


# vim:sw=4:ts=4:et:
