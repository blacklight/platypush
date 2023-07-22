"""
Platydock

Platydock is a helper that allows you to easily manage (create, destroy, start,
stop and list) Platypush instances as Docker images.
"""

import argparse
import enum
import os
import pathlib
import re
import shutil
import subprocess
import sys
import textwrap
import traceback as tb
import yaml

from platypush.config import Config
from platypush.utils import manifest

workdir = os.path.join(
    os.path.expanduser('~'), '.local', 'share', 'platypush', 'platydock'
)


class Action(enum.Enum):
    build = 'build'
    start = 'start'
    stop = 'stop'
    rm = 'rm'
    ls = 'ls'

    def __str__(self):
        return self.value


def _parse_deps(cls):
    deps = []

    for line in cls.__doc__.split('\n'):
        m = re.search(r'\(``pip install (.+)``\)', line)
        if m:
            deps.append(m.group(1))

    return deps


def generate_dockerfile(deps, ports, cfgfile, device_dir, python_version):
    device_id = Config.get('device_id')
    if not device_id:
        raise RuntimeError(
            (
                'You need to specify a device_id in {} - Docker '
                + 'containers cannot rely on hostname'
            ).format(cfgfile)
        )

    os.makedirs(device_dir, exist_ok=True)
    content = textwrap.dedent(
        '''
        FROM python:{python_version}-slim-bullseye

        RUN mkdir -p /app
        RUN mkdir -p /etc/platypush
        RUN mkdir -p /usr/local/share/platypush\n
        '''.format(
            python_version=python_version
        )
    ).lstrip()

    srcdir = os.path.dirname(cfgfile)
    cfgfile_copy = os.path.join(device_dir, 'config.yaml')
    shutil.copy(cfgfile, cfgfile_copy, follow_symlinks=True)
    content += 'COPY config.yaml /etc/platypush/\n'
    backend_config = Config.get_backends()

    # Redis configuration for Docker
    if 'redis' not in backend_config:
        backend_config['redis'] = {
            'redis_args': {
                'host': 'redis',
                'port': 6379,
            }
        }

        with open(cfgfile_copy, 'a') as f:
            f.write(
                '\n# Automatically added by platydock, do not remove\n'
                + yaml.dump(
                    {
                        'backend.redis': backend_config['redis'],
                    }
                )
                + '\n'
            )

    # Main database configuration
    has_main_db = False
    with open(cfgfile_copy, 'r') as f:
        for line in f.readlines():
            if re.match(r'^(main.)?db.*', line):
                has_main_db = True
                break

    if not has_main_db:
        with open(cfgfile_copy, 'a') as f:
            f.write(
                '\n# Automatically added by platydock, do not remove\n'
                + yaml.dump(
                    {
                        'main.db': {
                            'engine': 'sqlite:////platypush.db',
                        }
                    }
                )
                + '\n'
            )

    # Copy included files
    # noinspection PyProtectedMember
    for include in Config._included_files:
        incdir = os.path.relpath(os.path.dirname(include), srcdir)
        destdir = os.path.join(device_dir, incdir)
        pathlib.Path(destdir).mkdir(parents=True, exist_ok=True)
        shutil.copy(include, destdir, follow_symlinks=True)
        content += 'RUN mkdir -p /etc/platypush/' + incdir + '\n'
        content += (
            'COPY '
            + os.path.relpath(include, srcdir)
            + ' /etc/platypush/'
            + incdir
            + '\n'
        )

    # Copy script files
    scripts_dir = os.path.join(os.path.dirname(cfgfile), 'scripts')
    if os.path.isdir(scripts_dir):
        local_scripts_dir = os.path.join(device_dir, 'scripts')
        remote_scripts_dir = '/etc/platypush/scripts'
        shutil.copytree(
            scripts_dir, local_scripts_dir, symlinks=True, dirs_exist_ok=True
        )
        content += f'RUN mkdir -p {remote_scripts_dir}\n'
        content += f'COPY scripts/ {remote_scripts_dir}\n'

    packages = deps.pop('packages', None)
    pip = deps.pop('pip', None)
    exec_cmds = deps.pop('exec', None)
    pkg_cmd = (
        f'\n\t&& apt-get install --no-install-recommends -y {" ".join(packages)} \\'
        if packages
        else ''
    )
    pip_cmd = f'\n\t&& pip install {" ".join(pip)} \\' if pip else ''
    content += f'''
RUN dpkg --configure -a \\
    && apt-get -f install \\
    && apt-get --fix-missing install \\
    && apt-get clean \\
    && apt-get update \\
    && apt-get -y upgrade \\
    && apt-get -y dist-upgrade \\
    && apt-get install --no-install-recommends -y apt-utils \\
    && apt-get install --no-install-recommends -y build-essential \\
    && apt-get install --no-install-recommends -y git \\
    && apt-get install --no-install-recommends -y sudo \\
    && apt-get install --no-install-recommends -y libffi-dev \\
    && apt-get install --no-install-recommends -y libcap-dev \\
    && apt-get install --no-install-recommends -y libjpeg-dev \\{pkg_cmd}{pip_cmd}'''

    for exec_cmd in exec_cmds:
        content += f'\n\t&& {exec_cmd} \\'
    content += '''
    && apt-get install --no-install-recommends -y zlib1g-dev

RUN git clone --recursive https://git.platypush.tech/platypush/platypush.git /app \\
    && cd /app \\
    && pip install -r requirements.txt

RUN apt-get remove -y git \\
    && apt-get remove -y build-essential \\
    && apt-get remove -y libffi-dev \\
    && apt-get remove -y libjpeg-dev \\
    && apt-get remove -y libcap-dev \\
    && apt-get remove -y zlib1g-dev \\
    && apt-get remove -y apt-utils \\
    && apt-get clean \\
    && apt-get autoremove -y \\
    && rm -rf /var/lib/apt/lists/*
'''

    for port in ports:
        content += 'EXPOSE {}\n'.format(port)

    content += textwrap.dedent(
        '''

        ENV PYTHONPATH /app:$PYTHONPATH
        CMD ["python", "-m", "platypush"]
        '''
    )

    dockerfile = os.path.join(device_dir, 'Dockerfile')
    print('Generating Dockerfile {}'.format(dockerfile))

    with open(dockerfile, 'w') as f:
        f.write(content)


def build(args):
    global workdir

    ports = set()
    parser = argparse.ArgumentParser(
        prog='platydock build', description='Build a Platypush image from a config.yaml'
    )

    parser.add_argument(
        '-c',
        '--config',
        type=str,
        required=True,
        help='Path to the platypush configuration file',
    )
    parser.add_argument(
        '-p',
        '--python-version',
        type=str,
        default='3.9',
        help='Python version to be used',
    )

    opts, args = parser.parse_known_args(args)

    cfgfile = os.path.abspath(os.path.expanduser(opts.config))
    manifest._available_package_manager = (
        'apt'  # Force apt for Debian-based Docker images
    )
    install_cmds = manifest.get_dependencies_from_conf(cfgfile)
    python_version = opts.python_version
    backend_config = Config.get_backends()

    # Container exposed ports
    if backend_config.get('http'):
        from platypush.backend.http import HttpBackend

        # noinspection PyProtectedMember
        ports.add(backend_config['http'].get('port', HttpBackend._DEFAULT_HTTP_PORT))

    if backend_config.get('tcp'):
        ports.add(backend_config['tcp']['port'])

    dev_dir = os.path.join(workdir, Config.get('device_id'))
    generate_dockerfile(
        deps=dict(install_cmds),
        ports=ports,
        cfgfile=cfgfile,
        device_dir=dev_dir,
        python_version=python_version,
    )

    subprocess.call(
        [
            'docker',
            'build',
            '-t',
            'platypush-{}'.format(Config.get('device_id')),
            dev_dir,
        ]
    )


def start(args):
    global workdir

    parser = argparse.ArgumentParser(
        prog='platydock start',
        description='Start a Platypush container',
        epilog=textwrap.dedent(
            '''
                                       You can append additional options that
                                       will be passed to the docker container.
                                       Example:

                                            --add-host='myhost:192.168.1.1'
                                       '''
        ),
    )

    parser.add_argument('image', type=str, help='Platypush image to start')
    parser.add_argument(
        '-p',
        '--publish',
        action='append',
        nargs='*',
        default=[],
        help=textwrap.dedent(
            '''
                                             Container's ports to expose to the host.
                                             Note that the default exposed ports from
                                             the container service will be exposed unless
                                             these mappings override them (e.g. port 8008
                                             on the container will be mapped to 8008 on
                                             the host).

                                             Example:

                                             -p 18008:8008
                                             '''
        ),
    )

    parser.add_argument(
        '-a',
        '--attach',
        action='store_true',
        default=False,
        help=textwrap.dedent(
            '''
                                             If set, then attach to the container after starting it up (default: false).
                                             '''
        ),
    )

    opts, args = parser.parse_known_args(args)
    ports = {}
    dockerfile = os.path.join(workdir, opts.image, 'Dockerfile')

    with open(dockerfile) as f:
        for line in f:
            m = re.match(r'expose (\d+)', line.strip().lower())
            if m:
                ports[m.group(1)] = m.group(1)

    for mapping in opts.publish:
        host_port, container_port = mapping[0].split(':')
        ports[container_port] = host_port

    print('Preparing Redis support container')
    subprocess.call(['docker', 'pull', 'redis'])
    subprocess.call(
        ['docker', 'run', '--rm', '--name', 'redis-' + opts.image, '-d', 'redis']
    )

    docker_cmd = [
        'docker',
        'run',
        '--rm',
        '--name',
        opts.image,
        '-it',
        '--link',
        'redis-' + opts.image + ':redis',
    ]

    for container_port, host_port in ports.items():
        docker_cmd += ['-p', host_port + ':' + container_port]

    docker_cmd += args
    docker_cmd += ['-d', 'platypush-' + opts.image]

    print('Starting Platypush container {}'.format(opts.image))
    subprocess.call(docker_cmd)

    if opts.attach:
        subprocess.call(['docker', 'attach', opts.image])


def stop(args):
    parser = argparse.ArgumentParser(
        prog='platydock stop', description='Stop a Platypush container'
    )

    parser.add_argument('container', type=str, help='Platypush container to stop')
    opts, args = parser.parse_known_args(args)

    print('Stopping Platypush container {}'.format(opts.container))
    subprocess.call(['docker', 'kill', '{}'.format(opts.container)])

    print('Stopping Redis support container')
    subprocess.call(['docker', 'stop', 'redis-{}'.format(opts.container)])


def rm(args):
    global workdir

    parser = argparse.ArgumentParser(
        prog='platydock rm',
        description='Remove a Platypush image. '
        + 'NOTE: make sure that no container is '
        + 'running nor linked to the image before '
        + 'removing it',
    )

    parser.add_argument('image', type=str, help='Platypush image to remove')
    opts, args = parser.parse_known_args(args)

    subprocess.call(['docker', 'rmi', 'platypush-{}'.format(opts.image)])
    shutil.rmtree(os.path.join(workdir, opts.image), ignore_errors=True)


def ls(args):
    parser = argparse.ArgumentParser(
        prog='platydock ls', description='List available Platypush containers'
    )
    parser.add_argument('filter', type=str, nargs='?', help='Image name filter')

    opts, args = parser.parse_known_args(args)

    p = subprocess.Popen(['docker', 'images'], stdout=subprocess.PIPE)
    output = p.communicate()[0].decode().split('\n')
    header = output.pop(0)
    images = []

    for line in output:
        if re.match(r'^platypush-(.+?)\s.*', line) and (
            not opts.filter or (opts.filter and opts.filter in line)
        ):
            images.append(line)

    if images:
        print(header)

        for image in images:
            print(image)


def main():
    parser = argparse.ArgumentParser(
        prog='platydock',
        add_help=False,
        description='Manage Platypush docker containers',
        epilog='Use platydock <action> --help to ' + 'get additional help',
    )

    # noinspection PyTypeChecker
    parser.add_argument(
        'action', nargs='?', type=Action, choices=list(Action), help='Action to execute'
    )
    parser.add_argument('-h', '--help', action='store_true', help='Show usage')
    opts, args = parser.parse_known_args(sys.argv[1:])

    if (opts.help and not opts.action) or (not opts.help and not opts.action):
        parser.print_help()
        return 1

    globals()[str(opts.action)](sys.argv[2:])


if __name__ == '__main__':
    ERR_PREFIX = '\n\033[6;31;47mERROR\033[0;91m '
    ERR_SUFFIX = '\033[0m'

    try:
        main()
    except Exception as e:
        tb.print_exc(file=sys.stdout)
        print(ERR_PREFIX + str(e) + ERR_SUFFIX, file=sys.stderr)

# vim:sw=4:ts=4:et:
