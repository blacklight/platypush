import argparse
from typing import Sequence

from platypush.bus.redis import RedisBus
from platypush.utils import get_default_pid_file


def parse_cmdline(args: Sequence[str]) -> argparse.Namespace:
    """
    Parse command-line arguments from a list of strings.
    """
    parser = argparse.ArgumentParser(
        'platypush',
        description='A general-purpose platform for automation. See https://docs.platypush.tech for more info.',
    )

    parser.add_argument(
        '--config',
        '-c',
        dest='config',
        required=False,
        default=None,
        help='Custom location for the configuration file',
    )

    parser.add_argument(
        '--workdir',
        '-w',
        dest='workdir',
        required=False,
        default=None,
        help='Custom working directory to be used for the application',
    )

    parser.add_argument(
        '--main-db',
        '--db',
        dest='db_engine',
        required=False,
        default=None,
        help='Custom database engine to be used for the application '
        '(e.g. sqlite:///:memory: or sqlite:///path/to/db.sqlite). '
        'If missing, it falls back to the value of the `main.db` setting in the configuration file. '
        'If missing, it falls back to sqlite://<workdir>/main.db.',
    )

    parser.add_argument(
        '--cachedir',
        dest='cachedir',
        required=False,
        default=None,
        help='Custom cache directory',
    )

    parser.add_argument(
        '--device-id',
        '-d',
        dest='device_id',
        required=False,
        default=None,
        help='Override the device ID used to identify this instance. If not '
        'passed here, it is inferred from the configuration (device_id field).'
        'If not present there either, it is inferred from the hostname.',
    )

    parser.add_argument(
        '--logsdir',
        '-l',
        dest='logsdir',
        required=False,
        default=None,
        help='Store logs in the specified directory. By default, the '
        '`[logging.]filename` configuration option will be used. If not '
        'set, logging will be sent to stdout and stderr.',
    )

    parser.add_argument(
        '--version',
        dest='version',
        required=False,
        action='store_true',
        help="Print the current version and exit",
    )

    parser.add_argument(
        '--verbose',
        '-v',
        dest='verbose',
        required=False,
        action='store_true',
        help="Enable verbose/debug logging",
    )

    parser.add_argument(
        '--pidfile',
        '-P',
        dest='pidfile',
        required=False,
        default=get_default_pid_file(),
        help="File where platypush will "
        + "store its PID, useful if you're planning to "
        + f"integrate it in a service (default: {get_default_pid_file()})",
    )

    parser.add_argument(
        '--no-capture-stdout',
        dest='no_capture_stdout',
        required=False,
        action='store_true',
        help="Set this flag if you have max stack depth "
        + "exceeded errors so stdout won't be captured by "
        + "the logging system",
    )

    parser.add_argument(
        '--no-capture-stderr',
        dest='no_capture_stderr',
        required=False,
        action='store_true',
        help="Set this flag if you have max stack depth "
        + "exceeded errors so stderr won't be captured by "
        + "the logging system",
    )

    parser.add_argument(
        '--redis-queue',
        dest='redis_queue',
        required=False,
        default=RedisBus.DEFAULT_REDIS_QUEUE,
        help="Name of the Redis queue to be used to internally deliver messages "
        f"(default: {RedisBus.DEFAULT_REDIS_QUEUE})",
    )

    parser.add_argument(
        '--start-redis',
        dest='start_redis',
        required=False,
        action='store_true',
        help="Set this flag if you want to run and manage Redis internally "
        "from the app rather than using an external server. It requires the "
        "redis-server executable to be present in the path",
    )

    parser.add_argument(
        '--redis-host',
        dest='redis_host',
        required=False,
        default=None,
        help="Overrides the host specified in the redis section of the "
        "configuration file",
    )

    parser.add_argument(
        '--redis-port',
        dest='redis_port',
        required=False,
        default=None,
        help="Overrides the port specified in the redis section of the "
        "configuration file",
    )

    parser.add_argument(
        '--redis-bin',
        dest='redis_bin',
        required=False,
        default=None,
        help="Path to the redis-server executable, if --start-redis is "
        "specified. Drop-in replacements such as keydb-server, valkey or redict "
        "are also supported",
    )

    parser.add_argument(
        '--ctrl-sock',
        dest='ctrl_sock',
        required=False,
        default=None,
        help="If set, it identifies a path to a UNIX domain socket that "
        "the application can use to send control messages (e.g. STOP and "
        "RESTART) to its parent.",
    )

    opts, _ = parser.parse_known_args(args)
    return opts
