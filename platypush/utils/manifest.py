from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import importlib
import inspect
import json
import logging
import os
import pathlib
import re
import shutil
import subprocess
import sys

from typing import (
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Iterable,
    Mapping,
    Sequence,
    Set,
    Type,
    Union,
)
from typing_extensions import override

import yaml

from platypush.message.event import Event
from platypush.utils import get_src_root, is_root

_available_package_manager = None
logger = logging.getLogger(__name__)


class BaseImage(Enum):
    """
    Supported base images for Dockerfiles.
    """

    ALPINE = 'alpine'
    DEBIAN = 'debian'
    UBUNTU = 'ubuntu'

    def __str__(self) -> str:
        """
        Explicit __str__ override for argparse purposes.
        """
        return self.value


@dataclass
class PackageManager:
    """
    Representation of a package manager.
    """

    executable: str
    """ The executable name. """
    default_os: str
    """
    The default distro whose configuration we should use if this package
    manager is detected.
    """
    install: Sequence[str] = field(default_factory=tuple)
    """ The install command, as a sequence of strings. """
    uninstall: Sequence[str] = field(default_factory=tuple)
    """ The uninstall command, as a sequence of strings. """
    list: Sequence[str] = field(default_factory=tuple)
    """ The command to list the installed packages. """
    parse_list_line: Callable[[str], str] = field(default_factory=lambda: lambda s: s)
    """
    Internal package-manager dependent function that parses the base package
    name from a line returned by the list command.
    """

    def _get_installed(self) -> Sequence[str]:
        """
        :return: The install context-aware list of installed packages.
            It should only used within the context of :meth:`.get_installed`.
        """

        if os.environ.get('DOCKER_CTX'):
            # If we're running in a Docker build context, don't run the package
            # manager to retrieve the list of installed packages, as the host
            # and guest systems have different environments.
            return ()

        return tuple(
            line.strip()
            for line in subprocess.Popen(  # pylint: disable=consider-using-with
                self.list, stdout=subprocess.PIPE
            )
            .communicate()[0]
            .decode()
            .split('\n')
            if line.strip()
        )

    def get_installed(self) -> Sequence[str]:
        """
        :return: The list of installed packages.
        """
        return tuple(self.parse_list_line(line) for line in self._get_installed())


class PackageManagers(Enum):
    """
    Supported package managers.
    """

    APK = PackageManager(
        executable='apk',
        install=('apk', 'add', '--update', '--no-interactive', '--no-cache'),
        uninstall=('apk', 'del', '--no-interactive'),
        list=('apk', 'list', '--installed'),
        default_os='alpine',
        parse_list_line=lambda line: re.sub(r'.*\s*\{(.+?)\}\s*.*', r'\1', line),
    )

    APT = PackageManager(
        executable='apt',
        install=('apt', 'install', '-y'),
        uninstall=('apt', 'remove', '-y'),
        list=('apt', 'list', '--installed'),
        default_os='debian',
        parse_list_line=lambda line: line.split('/')[0],
    )

    PACMAN = PackageManager(
        executable='pacman',
        install=('pacman', '-S', '--noconfirm', '--needed'),
        uninstall=('pacman', '-R', '--noconfirm'),
        list=('pacman', '-Q'),
        default_os='arch',
        parse_list_line=lambda line: line.split(' ')[0],
    )

    @classmethod
    def get_command(cls, name: str) -> Iterable[str]:
        """
        :param name: The name of the package manager executable to get the
            command for.
        :return: The base command to execute, as a sequence of strings.
        """
        pkg_manager = next(iter(pm for pm in cls if pm.value.executable == name), None)
        if not pkg_manager:
            raise ValueError(f'Unknown package manager: {name}')

        return pkg_manager.value.install

    @classmethod
    def scan(cls) -> Optional["PackageManagers"]:
        """
        Get the name of the available package manager on the system, if supported.
        """
        # pylint: disable=global-statement
        global _available_package_manager
        if _available_package_manager:
            return _available_package_manager

        available_package_managers = [
            pkg_manager
            for pkg_manager in cls
            if shutil.which(pkg_manager.value.executable)
        ]

        if not available_package_managers:
            logger.warning(
                '\nYour OS does not provide any of the supported package managers.\n'
                'You may have to install some optional dependencies manually.\n'
                'Supported package managers: %s.\n',
                ', '.join([pm.value.executable for pm in cls]),
            )

            return None

        _available_package_manager = available_package_managers[0]
        return _available_package_manager


class InstallContext(Enum):
    """
    Supported installation contexts.
    """

    NONE = None
    DOCKER = 'docker'
    VENV = 'venv'


class ManifestType(Enum):
    """
    Manifest types.
    """

    PLUGIN = 'plugin'
    BACKEND = 'backend'


@dataclass
class Dependencies:
    """
    Dependencies for a plugin/backend.
    """

    before: List[str] = field(default_factory=list)
    """ Commands to execute before the component is installed. """
    packages: Set[str] = field(default_factory=set)
    """ System packages required by the component. """
    pip: Set[str] = field(default_factory=set)
    """ pip dependencies. """
    after: List[str] = field(default_factory=list)
    """ Commands to execute after the component is installed. """
    pkg_manager: Optional[PackageManagers] = None
    """ Override the default package manager detected on the system. """
    install_context: InstallContext = InstallContext.NONE
    """ The installation context - Docker, virtual environment or bare metal. """
    base_image: Optional[BaseImage] = None
    """ Base image used in case of Docker installations. """

    @property
    def _is_venv(self) -> bool:
        """
        :return: True if the dependencies scanning logic is running either in a
            virtual environment or in a virtual environment preparation
            context.
        """
        return (
            self.install_context == InstallContext.VENV or sys.prefix != sys.base_prefix
        )

    @property
    def _is_docker(self) -> bool:
        """
        :return: True if the dependencies scanning logic is running either in a
            Docker environment.
        """
        return (
            self.install_context == InstallContext.DOCKER
            or bool(os.environ.get('DOCKER_CTX'))
            or os.path.isfile('/.dockerenv')
        )

    @property
    def _wants_sudo(self) -> bool:
        """
        :return: True if the system dependencies should be installed with sudo.
        """
        return not (self._is_docker or is_root())

    @staticmethod
    def _get_requirements_dir() -> str:
        """
        :return: The root folder for the base installation requirements.
        """
        return os.path.join(get_src_root(), 'install', 'requirements')

    @classmethod
    def _parse_requirements_file(
        cls,
        requirements_file: str,
        install_context: InstallContext = InstallContext.NONE,
    ) -> Iterable[str]:
        """
        :param requirements_file: The path to the requirements file.
        :return: The list of requirements to install.
        """
        with open(requirements_file, 'r') as f:
            return {
                line.strip()
                for line in f
                if not (
                    not line.strip()
                    or line.strip().startswith('#')
                    # Virtual environments will install all the Python
                    # dependencies via pip, so we should skip them here
                    or (
                        install_context == InstallContext.VENV
                        and cls._is_python_pkg(line.strip())
                    )
                )
            }

    @classmethod
    def _get_base_system_dependencies(
        cls,
        pkg_manager: Optional[PackageManagers] = None,
        install_context: InstallContext = InstallContext.NONE,
    ) -> Iterable[str]:
        """
        :return: The base system dependencies that should be installed on the
            system.
        """

        # Docker images will install the base packages through their own
        # dedicated shell script, so don't report their base system
        # requirements here.
        if not (pkg_manager and install_context != InstallContext.DOCKER):
            return set()

        return cls._parse_requirements_file(
            os.path.join(
                cls._get_requirements_dir(), pkg_manager.value.default_os + '.txt'
            ),
            install_context,
        )

    @staticmethod
    def _is_python_pkg(pkg: str) -> bool:
        """
        Utility function that returns True if a given package is a Python
        system package. These should be skipped during a virtual
        environment installation, as the virtual environment will be
        installed via pip.
        """
        tokens = pkg.split('-')
        return len(tokens) > 1 and tokens[0] in {'py3', 'python3', 'python'}

    @classmethod
    def from_config(
        cls,
        conf_file: Optional[str] = None,
        pkg_manager: Optional[PackageManagers] = None,
        install_context: InstallContext = InstallContext.NONE,
        base_image: Optional[BaseImage] = None,
    ) -> "Dependencies":
        """
        Parse the required dependencies from a configuration file.
        """
        if not pkg_manager:
            pkg_manager = PackageManagers.scan()

        base_system_deps = cls._get_base_system_dependencies(
            pkg_manager=pkg_manager, install_context=install_context
        )

        deps = cls(
            packages=set(base_system_deps),
            pkg_manager=pkg_manager,
            install_context=install_context,
            base_image=base_image,
        )

        for manifest in Manifests.by_config(conf_file, pkg_manager=pkg_manager):
            deps.before += manifest.install.before
            deps.pip.update(manifest.install.pip)
            deps.packages.update(manifest.install.packages)
            deps.after += manifest.install.after

        return deps

    def to_pkg_install_commands(self) -> Generator[str, None, None]:
        """
        Generates the package manager commands required to install the given
        dependencies on the system.
        """

        wants_sudo = not (self._is_docker or is_root())
        pkg_manager = self.pkg_manager or PackageManagers.scan()

        if self.packages and pkg_manager:
            installed_packages = pkg_manager.value.get_installed()
            to_install = sorted(
                pkg
                for pkg in self.packages  # type: ignore
                if pkg not in installed_packages
                and not (
                    self.install_context == InstallContext.VENV
                    and self._is_python_pkg(pkg)
                )
            )

            if to_install:
                yield ' '.join(
                    [
                        *(['sudo'] if wants_sudo else []),
                        *pkg_manager.value.install,
                        *to_install,
                    ]
                )

    def to_pip_install_commands(self, full_command=True) -> Generator[str, None, None]:
        """
        Generates the pip commands required to install the given dependencies on
        the system.

        :param full_command: Whether to return the full pip command to execute
            (as a single string) or the list of packages that will be installed
            through another script.
        """
        wants_break_system_packages = not (
            # Docker installations shouldn't require --break-system-packages in
            # pip, except for Debian
            (self._is_docker and self.base_image != BaseImage.DEBIAN)
            # --break-system-packages has been introduced in Python 3.10
            or sys.version_info < (3, 11)
            # If we're in a virtual environment then we don't need
            # --break-system-packages
            or self._is_venv
        )

        if self.pip:
            deps = sorted(self.pip)
            if full_command:
                yield (
                    'pip install -U --no-input --no-cache-dir '
                    + (
                        '--break-system-packages '
                        if wants_break_system_packages
                        else ''
                    )
                    + ' '.join(deps)
                )
            else:
                for dep in deps:
                    yield dep

    def to_install_commands(self) -> Generator[str, None, None]:
        """
        Generates the commands required to install the given dependencies on
        this system.
        """
        for cmd in self.before:
            yield cmd

        for cmd in self.to_pkg_install_commands():
            yield cmd

        for cmd in self.to_pip_install_commands():
            yield cmd

        for cmd in self.after:
            yield cmd


class Manifest(ABC):
    """
    Base class for plugin/backend manifests.
    """

    def __init__(
        self,
        package: str,
        description: Optional[str] = None,
        install: Optional[Dict[str, Iterable[str]]] = None,
        events: Optional[Mapping] = None,
        pkg_manager: Optional[PackageManagers] = None,
        **_,
    ):
        self._pkg_manager = pkg_manager or PackageManagers.scan()
        self.description = description
        self.install = self._init_deps(install or {})
        self.events = self._init_events(events or {})
        self.package = package
        self.component_name = '.'.join(package.split('.')[2:])
        self.component = None

    @property
    @abstractmethod
    def manifest_type(self) -> ManifestType:
        """
        :return: The type of the manifest.
        """

    def _init_deps(self, install: Mapping[str, Iterable[str]]) -> Dependencies:
        deps = Dependencies()
        for key, items in install.items():
            if key == 'pip':
                deps.pip.update(items)
            elif key == 'before':
                deps.before += items
            elif key == 'after':
                deps.after += items
            elif self._pkg_manager and key == self._pkg_manager.value.executable:
                deps.packages.update(items)

        return deps

    @staticmethod
    def _init_events(
        events: Union[Iterable[str], Mapping[str, Optional[str]]]
    ) -> Dict[Type[Event], str]:
        evt_dict = events if isinstance(events, Mapping) else {e: None for e in events}
        ret = {}

        for evt_name, doc in evt_dict.items():
            evt_module_name, evt_class_name = evt_name.rsplit('.', 1)
            try:
                evt_module = importlib.import_module(evt_module_name)
                evt_class = getattr(evt_module, evt_class_name)
            except Exception as e:
                raise AssertionError(f'Could not load event {evt_name}: {e}') from e

            ret[evt_class] = doc or evt_class.__doc__

        return ret

    @classmethod
    def from_file(
        cls, filename: str, pkg_manager: Optional[PackageManagers] = None
    ) -> "Manifest":
        """
        Parse a manifest filename into a ``Manifest`` class.
        """
        with open(str(filename), 'r') as f:
            manifest = yaml.safe_load(f).get('manifest', {})

        assert 'type' in manifest, f'Manifest file {filename} has no type field'
        comp_type = ManifestType(manifest.pop('type'))
        manifest_class = cls.by_type(comp_type)
        return manifest_class(**manifest, pkg_manager=pkg_manager)

    @classmethod
    def by_type(cls, manifest_type: ManifestType) -> Type["Manifest"]:
        """
        :return: The manifest class corresponding to the given manifest type.
        """
        if manifest_type == ManifestType.PLUGIN:
            return PluginManifest
        if manifest_type == ManifestType.BACKEND:
            return BackendManifest

        raise ValueError(f'Unknown manifest type: {manifest_type}')

    def __repr__(self):
        """
        :return: A JSON serialized representation of the manifest.
        """
        return json.dumps(
            {
                'description': self.description,
                'install': self.install,
                'events': {
                    '.'.join([evt_type.__module__, evt_type.__name__]): doc
                    for evt_type, doc in self.events.items()
                },
                'type': self.manifest_type.value,
                'package': self.package,
                'component_name': self.component_name,
            }
        )


class PluginManifest(Manifest):
    """
    Plugin manifest.
    """

    @property
    @override
    def manifest_type(self) -> ManifestType:
        return ManifestType.PLUGIN


# pylint: disable=too-few-public-methods
class BackendManifest(Manifest):
    """
    Backend manifest.
    """

    @property
    @override
    def manifest_type(self) -> ManifestType:
        return ManifestType.BACKEND


class Manifests:
    """
    General-purpose manifests utilities.
    """

    @staticmethod
    def by_base_class(
        base_class: Type, pkg_manager: Optional[PackageManagers] = None
    ) -> Generator[Manifest, None, None]:
        """
        Get all the manifest files declared under the base path of a given class
        and parse them into :class:`Manifest` objects.
        """
        for mf in pathlib.Path(os.path.dirname(inspect.getfile(base_class))).rglob(
            'manifest.yaml'
        ):
            yield Manifest.from_file(str(mf), pkg_manager=pkg_manager)

    @staticmethod
    def by_config(
        conf_file: Optional[str] = None,
        pkg_manager: Optional[PackageManagers] = None,
    ) -> Generator[Manifest, None, None]:
        """
        Get all the manifest objects associated to the extensions declared in a
        given configuration file.
        """
        from platypush.config import Config

        conf_args = []
        if conf_file:
            conf_args.append(conf_file)

        Config.init(*conf_args)
        app_dir = get_src_root()

        for name in Config.get_backends().keys():
            yield Manifest.from_file(
                os.path.join(app_dir, 'backend', *name.split('.'), 'manifest.yaml'),
                pkg_manager=pkg_manager,
            )

        for name in Config.get_plugins().keys():
            yield Manifest.from_file(
                os.path.join(app_dir, 'plugins', *name.split('.'), 'manifest.yaml'),
                pkg_manager=pkg_manager,
            )
