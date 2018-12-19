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

import platypush

from platypush.config import Config
from platypush.context import register_backends, get_plugin, get_backend


workdir = os.path.join(os.environ['HOME'], '.local', 'share',
                       'platypush', 'platydock')

class Action(enum.Enum):
    build = 'build'
    start = 'start'
    stop  = 'stop'
    rm    = 'rm'
    ls    = 'ls'

    def __str__(self):
        return self.value


def _parse_deps(cls):
    deps = []

    for line in cls.__doc__.split('\n'):
        m = re.search('\(``pip install (.+)``\)', line)
        if m:
            deps.append(m.group(1))

    return deps

def generate_dockerfile(deps, ports, cfgfile, devdir):
    device_id = Config.get('device_id')
    if not device_id:
        raise RuntimeError(('You need to specify a device_id in {} - Docker ' +
                           'containers cannot rely on hostname').format(cfgfile))

    try:
        os.makedirs(devdir)
    except FileExistsError:
        pass

    content = textwrap.dedent(
        '''
        FROM python:alpine3.7

        RUN mkdir -p /etc/platypush
        RUN mkdir -p /usr/local/share/platypush\n
        ''').lstrip()

    cfgfile_copy = os.path.join(devdir, 'config.yaml')
    with open(cfgfile) as src_f:
        with open(cfgfile_copy, 'w') as dest_f:
            for line in src_f:
                dest_f.write(line)

    content += 'COPY config.yaml /etc/platypush/'

    content += textwrap.dedent(
        '''
        RUN apk add --update --no-cache --virtual build-base \\
            && apk add --update --no-cache --virtual git \\
        ''')

    for dep in deps:
        content += '\t&& pip install {} \\\n'.format(dep)

    content += '\t&& pip install ' + \
        'git+https://github.com/BlackLight/platypush.git \\\n'

    content += '\t&& apk del git \\\n'
    content += '\t&& apk del build-base\n\n'

    for port in ports:
        content += 'EXPOSE {}\n'.format(port)

    content += '\nCMD ["python", "-m", "platypush"]\n'
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

    opts, args = parser.parse_known_args(args)

    cfgfile = os.path.abspath(os.path.expanduser(opts.config))
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
        except:
            pass

    devdir = os.path.join(workdir, Config.get('device_id'))
    generate_dockerfile(deps=deps, ports=ports, cfgfile=cfgfile, devdir=devdir)

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

    devdir = os.path.join(workdir, Config.get('device_id'))
    subprocess.call(['docker', 'rmi', 'platypush-{}'.format(opts.image)])
    subprocess.call(['rm', '-r', 'platypush-{}'.format(opts.image)])


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
