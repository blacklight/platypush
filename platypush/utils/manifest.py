from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import importlib
import inspect
import json
import logging
import os
import pathlib
import shutil
import sys

from typing import (
    Dict,
    Generator,
    List,
    Optional,
    Iterable,
    Mapping,
    Set,
    Type,
    Union,
)
from typing_extensions import override

import yaml

from platypush.message.event import Event

_available_package_manager = None
logger = logging.getLogger(__name__)


@dataclass
class PackageManager:
    """
    Representation of a package manager.
    """

    executable: str
    """ The executable name. """
    command: Iterable[str] = field(default_factory=tuple)
    """ The command to execute, as a sequence of strings. """


class PackageManagers(Enum):
    """
    Supported package managers.
    """

    APK = PackageManager(
        executable='apk',
        command=('apk', 'add', '--update', '--no-interactive', '--no-cache'),
    )

    APT = PackageManager(
        executable='apt',
        command=('DEBIAN_FRONTEND=noninteractive', 'apt', 'install', '-y'),
    )

    PACMAN = PackageManager(
        executable='pacman',
        command=('pacman', '-S', '--noconfirm'),
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

        return pkg_manager.value.command

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

    @classmethod
    def from_config(
        cls,
        conf_file: Optional[str] = None,
        pkg_manager: Optional[PackageManagers] = None,
        install_context: InstallContext = InstallContext.NONE,
    ) -> "Dependencies":
        """
        Parse the required dependencies from a configuration file.
        """
        deps = cls(pkg_manager=pkg_manager, install_context=install_context)

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
        wants_sudo = self.install_context != InstallContext.DOCKER and os.getuid() != 0
        pkg_manager = self.pkg_manager or PackageManagers.scan()
        if self.packages and pkg_manager:
            yield ' '.join(
                [
                    *(['sudo'] if wants_sudo else []),
                    *pkg_manager.value.command,
                    *sorted(self.packages),  # type: ignore
                ]
            )

    def to_pip_install_commands(self) -> Generator[str, None, None]:
        """
        Generates the pip commands required to install the given dependencies on
        the system.
        """
        wants_break_system_packages = not (
            # Docker installations shouldn't require --break-system-packages in pip
            self.install_context == InstallContext.DOCKER
            # --break-system-packages has been introduced in Python 3.10
            or sys.version_info < (3, 11)
            # If we're in a virtual environment then we don't need
            # --break-system-packages
            or self._is_venv
        )

        if self.pip:
            yield (
                'pip install -U --no-input --no-cache-dir '
                + ('--break-system-packages ' if wants_break_system_packages else '')
                + ' '.join(sorted(self.pip))
            )

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
        import platypush
        from platypush.config import Config

        conf_args = []
        if conf_file:
            conf_args.append(conf_file)

        Config.init(*conf_args)
        app_dir = os.path.dirname(inspect.getfile(platypush))

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
