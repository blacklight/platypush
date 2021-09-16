import enum
import inspect
import json
import logging
import os
import pathlib
import shutil
import yaml

from abc import ABC, abstractmethod
from typing import Optional, Iterable, Mapping, Callable, Type

supported_package_managers = {
    'pacman': 'pacman -S',
    'apt': 'apt-get install',
}

_available_package_manager = None


class ManifestType(enum.Enum):
    PLUGIN = 'plugin'
    BACKEND = 'backend'


class Manifest(ABC):
    """
    Base class for plugin/backend manifests.
    """
    def __init__(self, package: str, description: Optional[str] = None,
                 install: Optional[Iterable[str]] = None, events: Optional[Mapping] = None, **_):
        self.description = description
        self.install = install or {}
        self.events = events or {}
        self.logger = logging.getLogger(__name__)
        self.package = package
        self.component_name = '.'.join(package.split('.')[2:])
        self.component = None

    @classmethod
    @property
    @abstractmethod
    def component_getter(self) -> Callable[[str], object]:
        raise NotImplementedError

    @classmethod
    def from_file(cls, filename: str) -> "Manifest":
        with open(str(filename), 'r') as f:
            manifest = yaml.safe_load(f).get('manifest', {})

        assert 'type' in manifest, f'Manifest file {filename} has no type field'
        comp_type = ManifestType(manifest.pop('type'))
        manifest_class = _manifest_class_by_type[comp_type]
        return manifest_class(**manifest)

    @classmethod
    def from_class(cls, clazz) -> "Manifest":
        return cls.from_file(os.path.dirname(inspect.getfile(clazz)))

    @classmethod
    def from_component(cls, comp) -> "Manifest":
        return cls.from_class(comp.__class__)

    def get_component(self):
        try:
            self.component = self.component_getter(self.component_name)
        except Exception as e:
            self.logger.warning(f'Could not load {self.component_name}: {e}')

        return self.component

    def __repr__(self):
        return json.dumps({
            'description': self.description,
            'install': self.install,
            'events': self.events,
            'type': _manifest_type_by_class[self.__class__].value,
            'package': self.package,
            'component_name': self.component_name,
        })


class PluginManifest(Manifest):
    @classmethod
    @property
    def component_getter(self):
        from platypush.context import get_plugin
        return get_plugin


class BackendManifest(Manifest):
    @classmethod
    @property
    def component_getter(self):
        from platypush.context import get_backend
        return get_backend


_manifest_class_by_type: Mapping[ManifestType, Type[Manifest]] = {
    ManifestType.PLUGIN: PluginManifest,
    ManifestType.BACKEND: BackendManifest,
}

_manifest_type_by_class: Mapping[Type[Manifest], ManifestType] = {
    cls: t for t, cls in _manifest_class_by_type.items()
}


def scan_manifests(base_class: Type) -> Iterable[str]:
    for mf in pathlib.Path(os.path.dirname(inspect.getfile(base_class))).rglob('manifest.yaml'):
        yield str(mf)


def get_manifests(base_class: Type) -> Iterable[Manifest]:
    return [
        Manifest.from_file(mf)
        for mf in scan_manifests(base_class)
    ]


def get_components(base_class: Type) -> Iterable:
    manifests = get_manifests(base_class)
    components = {mf.get_component() for mf in manifests}
    return {comp for comp in components if comp is not None}


def get_manifests_from_conf(conf_file: Optional[str] = None) -> Mapping[str, Manifest]:
    import platypush
    from platypush.config import Config

    conf_args = []
    if conf_file:
        conf_args.append(conf_file)

    Config.init(*conf_args)
    app_dir = os.path.dirname(inspect.getfile(platypush))
    manifest_files = set()

    for name in Config.get_backends().keys():
        manifest_files.add(os.path.join(app_dir, 'backend', *name.split('.'), 'manifest.yaml'))

    for name in Config.get_plugins().keys():
        manifest_files.add(os.path.join(app_dir, 'plugins', *name.split('.'), 'manifest.yaml'))

    return {
        manifest_file: Manifest.from_file(manifest_file)
        for manifest_file in manifest_files
    }


def get_dependencies_from_conf(conf_file: Optional[str] = None) -> Mapping[str, Iterable[str]]:
    manifests = get_manifests_from_conf(conf_file)
    deps = {
        'pip': set(),
        'packages': set(),
        'exec': set(),
    }

    for manifest in manifests.values():
        deps['pip'].update(manifest.install.get('pip', set()))
        deps['exec'].update(manifest.install.get('exec', set()))
        has_requires_packages = len([
            section for section in manifest.install.keys()
            if section in supported_package_managers
        ]) > 0

        if has_requires_packages:
            pkg_manager = get_available_package_manager()
            deps['packages'].update(manifest.install.get(pkg_manager, set()))

    return deps


def get_install_commands_from_conf(conf_file: Optional[str] = None) -> Mapping[str, str]:
    deps = get_dependencies_from_conf(conf_file)
    return {
        'pip': f'pip install {" ".join(deps["pip"])}',
        'exec': deps["exec"],
        'packages': f'{supported_package_managers[_available_package_manager]} {" ".join(deps["packages"])}'
        if deps['packages'] else None,
    }


def get_available_package_manager() -> str:
    global _available_package_manager
    if _available_package_manager:
        return _available_package_manager

    available_package_managers = [
        pkg_manager for pkg_manager in supported_package_managers.keys()
        if shutil.which(pkg_manager)
    ]

    assert available_package_managers, (
        'Your OS does not provide any of the supported package managers. '
        f'Supported package managers: {supported_package_managers.keys()}'
    )

    _available_package_manager = available_package_managers[0]
    return _available_package_manager
