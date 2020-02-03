"""
Platydock

Platydock is a helper that allows you to easily manage (create, destroy, start,
stop and list) Platypush instances as Docker images.

.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
.. license: MIT
"""

import argparse
import enum
import os
import re
import subprocess
import sys
import textwrap
import traceback as tb

from platypush.config import Config
from platypush.context import register_backends, get_plugin, get_backend

workdir = os.path.join(os.path.expanduser('~'), '.local', 'share',
                       'platypush', 'platydock')


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
        m = re.search('\(``pip install (.+)``\)', line)
        if m:
            deps.append(m.group(1))

    return deps


def generate_dockerfile(deps, ports, cfgfile, devdir, python_version):
    device_id = Config.get('device_id')
    if not device_id:
        raise RuntimeError(('You need to specify a device_id in {} - Docker ' +
                            'containers cannot rely on hostname').format(cfgfile))

    os.makedirs(devdir, exist_ok=True)
    content = textwrap.dedent(
        '''
        FROM python:{python_version}-slim-buster

        RUN mkdir -p /app
        RUN mkdir -p /etc/platypush
        RUN mkdir -p /usr/local/share/platypush\n
        '''.format(python_version=python_version)).lstrip()

    srcdir = os.path.dirname(cfgfile)
    cfgfile_copy = os.path.join(devdir, 'config.yaml')
    subprocess.call(['cp', cfgfile, cfgfile_copy])
    content += 'COPY config.yaml /etc/platypush/\n'

    # noinspection PyProtectedMember
    for include in Config._included_files:
        incdir = os.path.relpath(os.path.dirname(include), srcdir)
        destdir = os.path.join(devdir, incdir)

        try:
            os.makedirs(destdir)
        except FileExistsError:
            pass

        subprocess.call(['cp', include, destdir])
        content += 'RUN mkdir -p /etc/platypush/' + incdir + '\n'
        content += 'COPY ' + os.path.relpath(include, srcdir) + \
                   ' /etc/platypush/' + incdir + '\n'

    content += textwrap.dedent(
        '''
        RUN dpkg --configure -a \\
            && apt-get -f install \\
            && apt-get --fix-missing install \\
            && apt-get clean \\
            && apt-get update \\
            && apt-get -y upgrade \\
            && apt-get -y dist-upgrade \\
            && apt-get install --no-install-recommends -y apt-utils\\
            && apt-get install --no-install-recommends -y build-essential \\
            && apt-get install --no-install-recommends -y git \\
            && apt-get install --no-install-recommends -y libffi-dev \\
            && apt-get install --no-install-recommends -y libjpeg-dev \\
            && apt-get install --no-install-recommends -y zlib1g-dev \\
        ''')

    for i, dep in enumerate(deps):
        content += '\t&& pip install --no-cache-dir {}'.format(dep)
        if i < len(deps)-1:
            content += ' \\'.format(dep)
        content += '\n'

    content += textwrap.dedent(
        '''

        RUN git clone --recursive https://github.com/BlackLight/platypush.git /app \\
            && cd /app \\
            && pip install -r requirements.txt \\
            && python setup.py web_build

        RUN apt-get remove -y git \\
            && apt-get remove -y build-essential \\
            && apt-get remove -y libffi-dev \\
            && apt-get remove -y libjpeg-dev \\
            && apt-get remove -y zlib1g-dev \\
            && apt-get remove -y apt-utils \\
            && apt-get clean \\
            && apt-get autoremove -y \\
            && rm -rf /var/lib/apt/lists/*

        ''')

    for port in ports:
        content += 'EXPOSE {}\n'.format(port)

    content += textwrap.dedent(
        '''

        ENV PYTHONPATH /app:$PYTHONPATH
        CMD ["python", "-m", "platypush"]
        ''')

    dockerfile = os.path.join(devdir, 'Dockerfile')
    print('Generating Dockerfile {}'.format(dockerfile))

    with open(dockerfile, 'w') as f:
        f.write(content)


def build(args):
    global workdir

    ports = set()
    deps = set()

    parser = argparse.ArgumentParser(prog='platydock build',
                                     description='Build a Platypush image ' +
                                                 'from a config.yaml')

    parser.add_argument('-c', '--config', type=str, required=True,
                        help='Path to the platypush configuration file')
    parser.add_argument('-p', '--python-version', type=str, default='3.8',
                        help='Python version to be used')

    opts, args = parser.parse_known_args(args)

    cfgfile = os.path.abspath(os.path.expanduser(opts.config))
    python_version = opts.python_version
    Config.init(cfgfile)
    register_backends()
    backend_config = Config.get_backends()

    if backend_config.get('http'):
        http_backend = get_backend('http')
        ports.add(http_backend.port)
        if http_backend.websocket_port:
            ports.add(http_backend.websocket_port)

    if backend_config.get('tcp'):
        ports.add(get_backend('tcp').port)

    if backend_config.get('websocket'):
        ports.add(get_backend('websocket').port)

    for name in Config.get_backends().keys():
        deps.update(_parse_deps(get_backend(name)))

    for name in Config.get_plugins().keys():
        try:
            deps.update(_parse_deps(get_plugin(name)))
        except Exception as ex:
            print('Dependencies parsing error for {}: {}'.format(name, str(ex)))

    devdir = os.path.join(workdir, Config.get('device_id'))
    generate_dockerfile(deps=deps, ports=ports, cfgfile=cfgfile, devdir=devdir, python_version=python_version)

    subprocess.call(['docker', 'build', '-t', 'platypush-{}'.format(
        Config.get('device_id')), devdir])


def start(args):
    global workdir

    parser = argparse.ArgumentParser(prog='platydock start',
                                     description='Start a Platypush container',
                                     epilog=textwrap.dedent('''
                                       You can append additional options that
                                       will be passed to the docker container.
                                       Example:

                                            --add-host='myhost:192.168.1.1'
                                       '''))

    parser.add_argument('image', type=str, help='Platypush image to start')
    parser.add_argument('-p', '--publish', action='append', nargs='*', default=[],
                        help=textwrap.dedent('''
                                             Container's ports to expose to the host.
                                             Note that the default exposed ports from
                                             the container service will be exposed unless
                                             these mappings override them (e.g. port 8008
                                             on the container will be mapped to 8008 on
                                             the host).

                                             Example:

                                             -p 18008:8008 -p 18009:8009
                                             '''))

    parser.add_argument('-a', '--attach', action='store_true', default=False,
                        help=textwrap.dedent('''
                                             If set, then attach to the container after starting it up (default: false).
                                             '''))


    opts, args = parser.parse_known_args(args)
    ports = {}
    dockerfile = os.path.join(workdir, opts.image, 'Dockerfile')

    with open(dockerfile) as f:
        for line in f:
            m = re.match('expose (\d+)', line.strip().lower())
            if m:
                ports[m.group(1)] = m.group(1)

    for mapping in opts.publish:
        host_port, container_port = mapping[0].split(':')
        ports[container_port] = host_port

    print('Preparing Redis support container')
    subprocess.call(['docker', 'pull', 'redis'])
    subprocess.call(['docker', 'run', '--rm', '--name', 'redis-' + opts.image,
                     '-d', 'redis'])

    docker_cmd = ['docker', 'run', '--rm', '--name', opts.image, '-it',
                  '--link', 'redis-' + opts.image + ':redis']

    for container_port, host_port in ports.items():
        docker_cmd += ['-p', host_port + ':' + container_port]

    docker_cmd += args
    docker_cmd += ['-d', 'platypush-' + opts.image]

    print('Starting Platypush container {}'.format(opts.image))
    subprocess.call(docker_cmd)

    if opts.attach:
        subprocess.call(['docker', 'attach', opts.image])


def stop(args):
    parser = argparse.ArgumentParser(prog='platydock stop',
                                     description='Stop a Platypush container')

    parser.add_argument('container', type=str, help='Platypush container to stop')
    opts, args = parser.parse_known_args(args)

    print('Stopping Platypush container {}'.format(opts.container))
    subprocess.call(['docker', 'kill', '{}'.format(opts.container)])

    print('Stopping Redis support container')
    subprocess.call(['docker', 'stop', 'redis-{}'.format(opts.container)])


def rm(args):
    global workdir

    parser = argparse.ArgumentParser(prog='platydock rm',
                                     description='Remove a Platypush image. ' +
                                                 'NOTE: make sure that no container is ' +
                                                 'running nor linked to the image before ' +
                                                 'removing it')

    parser.add_argument('image', type=str, help='Platypush image to remove')
    opts, args = parser.parse_known_args(args)

    subprocess.call(['docker', 'rmi', 'platypush-{}'.format(opts.image)])
    subprocess.call(['rm', '-r', os.path.join(workdir, opts.image)])


def ls(args):
    parser = argparse.ArgumentParser(prog='platydock ls',
                                     description='List available Platypush containers')
    parser.add_argument('filter', type=str, nargs='?',
                        help='Image name filter')

    opts, args = parser.parse_known_args(args)

    p = subprocess.Popen(['docker', 'images'], stdout=subprocess.PIPE)
    output = p.communicate()[0].decode().split('\n')
    header = output.pop(0)
    images = []

    for line in output:
        if re.match('^platypush-(.+?)\s.*', line):
            if not opts.filter or (opts.filter and opts.filter in line):
                images.append(line)

    if images:
        print(header)

        for image in images:
            print(image)


def main():
    parser = argparse.ArgumentParser(prog='platydock', add_help=False,
                                     description='Manage Platypush docker containers',
                                     epilog='Use platydock <action> --help to ' +
                                            'get additional help')

    # noinspection PyTypeChecker
    parser.add_argument('action', nargs='?', type=Action, choices=list(Action),
                        help='Action to execute')
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
