import argparse
import os
import re
import sys
import textwrap as tw
from typing import List, Optional

import httplib2
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from platypush.config import Config

credentials_dir = os.path.join(Config.get_workdir(), "credentials", "google")
default_secrets_file = os.path.join(credentials_dir, "client_secret.json")
"""Default path for the Google API client secrets file"""


def _parse_scopes(*scopes: str) -> List[str]:
    return sorted(
        {
            t.split("/")[-1].strip()
            for scope in scopes
            for t in re.split(r"[\s,]", scope)
            if t
        }
    )


def get_credentials_filename(*scopes: str):
    parsed_scopes = _parse_scopes(*scopes)
    scope_name = "-".join([scope.split("/")[-1] for scope in parsed_scopes])
    os.makedirs(credentials_dir, exist_ok=True)
    matching_scope_file = next(
        iter(
            os.path.join(credentials_dir, scopes_file)
            for scopes_file in {
                os.path.basename(file)
                for file in os.listdir(credentials_dir)
                if file.endswith(".json")
            }
            if not set(parsed_scopes).difference(
                set(scopes_file.split(".json")[0].split("-"))
            )
        ),
        None,
    )

    if matching_scope_file:
        return matching_scope_file

    return os.path.join(credentials_dir, scope_name + ".json")


def get_credentials(scope: str, secrets_file: Optional[str] = None):
    scopes = _parse_scopes(scope)
    credentials_file = get_credentials_filename(*scopes)

    # If we don't have a credentials file for the required set of scopes, but we have a secrets file,
    # then try and generate the credentials file from the stored secrets.
    if (
        not os.path.isfile(credentials_file)
        and secrets_file
        and os.path.isfile(secrets_file)
        and (os.getenv("DISPLAY") or os.getenv("BROWSER"))
    ):
        args = []
        generate_credentials(secrets_file, scope, *args)

    assert os.path.isfile(credentials_file), tw.dedent(
        f"""
        Credentials file {credentials_file} not found. Generate it through:
            python -m platypush.plugins.google.credentials "{','.join(scopes)}" {
                secrets_file or '/path/to/client_secret.json'
            }
              [--auth_host_name AUTH_HOST_NAME]
              [--noauth_local_webserver]
              [--auth_host_port [AUTH_HOST_PORT [AUTH_HOST_PORT ...]]]
              [--logging_level [DEBUG,INFO,WARNING,ERROR,CRITICAL]]

        Specify --noauth_local_webserver if you're running this script on a headless machine.
        You will then get an authentication URL on the logs.
        Otherwise, the URL will be opened in the available browser.
        """
    )

    store = Storage(credentials_file)
    credentials = store.get()

    if not credentials or credentials.invalid:
        credentials.refresh(httplib2.Http())

    return credentials


def generate_credentials(client_secret_path: str, scope: str, *args: str):
    scopes = _parse_scopes(scope)
    credentials_file = get_credentials_filename(*scopes)
    store = Storage(credentials_file)
    scope = ' '.join(
        f'https://www.googleapis.com/auth/{scope}' for scope in _parse_scopes(scope)
    )

    flow = client.flow_from_clientsecrets(client_secret_path, scope)
    flow.user_agent = "Platypush"
    flow.access_type = "offline"  # type: ignore
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args(args)  # type: ignore
    tools.run_flow(flow, store, flags)
    print("Storing credentials to", credentials_file)
    print(
        "\nIf this is not the working directory of your Platypush instance, \n"
        "then move the generated credentials file to WORKDIR/credentials/google"
    )


def main():
    """
    Generates a Google API credentials file given client secret JSON and scopes.
    Usage::

        python -m platypush.plugins.google.credentials \
            [spaces/comma-separated list of scopes] \
            [client_secret.json location]

    """

    args = sys.argv[1:]
    scope = (
        args.pop(0) if args else input("Space/comma separated list of OAuth scopes: ")
    ).strip()

    if args:
        client_secret_path = args.pop(0)
    elif os.path.isfile(default_secrets_file):
        client_secret_path = default_secrets_file
    else:
        client_secret_path = input("Google credentials JSON file location: ")

    client_secret_path = os.path.abspath(os.path.expanduser(client_secret_path)).strip()
    generate_credentials(client_secret_path, scope, *args)


if __name__ == "__main__":
    main()

# vim:sw=4:ts=4:et:
