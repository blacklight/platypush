import argparse
import httplib2
import os
import sys

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


def get_credentials_filename(*scopes):
    from platypush.config import Config

    scope_name = '-'.join([scope.split('/')[-1] for scope in scopes])
    credentials_dir = os.path.join(
        Config.get('workdir'), 'credentials', 'google')

    os.makedirs(credentials_dir, exist_ok=True)
    return os.path.join(credentials_dir, scope_name + '.json')


def get_credentials(scope):
    credentials_file = get_credentials_filename(*sorted(scope.split(' ')))
    if not os.path.exists(credentials_file):
        raise RuntimeError(('Credentials file {} not found. Generate it through:\n' +
                           '\tpython -m platypush.plugins.google.credentials "{}" ' +
                           '<path to client_secret.json>\n' +
                           '\t\t[--auth_host_name AUTH_HOST_NAME]\n' +
                           '\t\t[--noauth_local_webserver]\n' +
                           '\t\t[--auth_host_port [AUTH_HOST_PORT [AUTH_HOST_PORT ...]]]\n' +
                           '\t\t[--logging_level [DEBUG,INFO,WARNING,ERROR,CRITICAL]]\n').
                           format(credentials_file, scope))

    store = Storage(credentials_file)
    credentials = store.get()

    if not credentials or credentials.invalid:
        credentials.refresh(httplib2.Http())

    return credentials


def generate_credentials(client_secret_path, scope):
    credentials_file = get_credentials_filename(*sorted(scope.split(' ')))
    store = Storage(credentials_file)

    flow = client.flow_from_clientsecrets(client_secret_path, scope)
    flow.user_agent = 'Platypush'
    flow.access_type = 'offline'
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    credentials = tools.run_flow(flow, store, flags)
    print('Storing credentials to ' + credentials_file)


def main():
    """
    Generates a Google API credentials file given client secret JSON and scopes.
    Usage::

        python -m platypush.plugins.google.credentials [client_secret.json location] [comma-separated list of scopes]
    """

    scope = sys.argv.pop(1) if len(sys.argv) > 1 \
              else input('Space separated list of OAuth scopes: ')

    client_secret_path = os.path.expanduser(
        sys.argv.pop(1) if len(sys.argv) > 1
        else input('Google credentials JSON file location: '))

    # Uncomment to force headless (no browser spawned) authentication
    # sys.argv.append('--noauth_local_webserver')

    generate_credentials(client_secret_path, scope)


if __name__ == '__main__':
    main()


# vim:sw=4:ts=4:et:

