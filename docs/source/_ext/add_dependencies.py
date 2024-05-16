import inspect
import os
import re
import sys
import textwrap as tw

from sphinx.application import Sphinx

base_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.relpath(__file__)), '..', '..', '..')
)

sys.path.insert(0, base_path)

from platypush.common.reflection import Integration  # noqa: E402
from platypush.utils import get_plugin_name_by_class  # noqa: E402
from platypush.utils.mock import auto_mocks  # noqa: E402


class IntegrationEnricher:
    @staticmethod
    def add_events(source: list[str], manifest: Integration, idx: int) -> int:
        if not manifest.events:
            return idx

        source.insert(
            idx,
            'Triggered events\n----------------\n\n'
            + '\n'.join(
                f'\t- :class:`{event.__module__}.{event.__qualname__}`'
                for event in manifest.events
            )
            + '\n\n',
        )

        return idx + 1

    @staticmethod
    def add_actions(source: list[str], manifest: Integration, idx: int) -> int:
        if not (manifest.actions and manifest.cls):
            return idx

        source.insert(
            idx,
            'Actions\n-------\n\n'
            + '\n'.join(
                f'\t- `{get_plugin_name_by_class(manifest.cls)}.{action} '
                + f'<#{manifest.cls.__module__}.{manifest.cls.__qualname__}.{action}>`_'
                for action in sorted(manifest.actions.keys())
            )
            + '\n\n',
        )

        return idx + 1

    @staticmethod
    def _shellify(title: str, cmd: str) -> str:
        return (
            f'**{title}**\n\n'
            + '.. code-block:: bash\n\n'
            + tw.indent(cmd, '\t')
            + '\n\n'
        )

    @classmethod
    def add_install_deps(
        cls, source: list[str], manifest: Integration, idx: int
    ) -> int:
        deps = manifest.deps
        parsed_deps = {
            'before': deps.before,
            'pip': deps.pip,
            'after': deps.after,
        }

        if not (any(parsed_deps.values()) or deps.by_pkg_manager):
            return idx

        source.insert(idx, 'Dependencies\n------------\n\n')
        idx += 1

        if parsed_deps['before']:
            source.insert(idx, cls._shellify('Pre-install', '\n'.join(deps.before)))
            idx += 1

        if parsed_deps['pip']:
            source.insert(
                idx, cls._shellify('pip', 'pip install ' + ' '.join(deps.pip))
            )
            idx += 1

        for pkg_manager, sys_deps in deps.by_pkg_manager.items():
            if not sys_deps:
                continue

            source.insert(
                idx,
                cls._shellify(
                    pkg_manager.value.default_os.value.description,
                    pkg_manager.value.install_doc + ' ' + ' '.join(sys_deps),
                ),
            )

            idx += 1

        if parsed_deps['after']:
            source.insert(idx, cls._shellify('Post-install', '\n'.join(deps.after)))
            idx += 1

        return idx

    @classmethod
    def add_description(cls, source: list[str], manifest: Integration, idx: int) -> int:
        docs = (
            doc
            for doc in (
                inspect.getdoc(manifest.cls) or '',
                manifest.constructor.doc if manifest.constructor else '',
            )
            if doc
        )

        if not docs:
            return idx

        docstring = '\n\n'.join(docs)
        source.insert(idx, f"Description\n-----------\n\n{docstring}\n\n")
        return idx + 1

    @classmethod
    def add_conf_snippet(
        cls, source: list[str], manifest: Integration, idx: int
    ) -> int:
        source.insert(
            idx,
            tw.dedent(
                f"""
                Configuration
                -------------

                .. code-block:: yaml

{tw.indent(manifest.config_snippet, '                  ')}
                """
            ),
        )

        return idx + 1

    def __call__(self, _: Sphinx, doc: str, source: list[str]):
        if not (source and re.match(r'^platypush/(backend|plugins)/.*', doc)):
            return

        src = [src.split('\n') for src in source][0]
        if len(src) < 3:
            return

        manifest_file = os.path.join(
            base_path,
            *doc.split(os.sep)[:-1],
            *doc.split(os.sep)[-1].split('.'),
            'manifest.json',
        )

        if not os.path.isfile(manifest_file):
            return

        with auto_mocks():
            manifest = Integration.from_manifest(manifest_file)
            idx = self.add_description(src, manifest, idx=3)
            idx = self.add_conf_snippet(src, manifest, idx=idx)
            idx = self.add_install_deps(src, manifest, idx=idx)
            idx = self.add_events(src, manifest, idx=idx)
            idx = self.add_actions(src, manifest, idx=idx)

        src.insert(idx, '\n\nModule reference\n----------------\n\n')
        source[0] = '\n'.join(src)


def setup(app: Sphinx):
    app.connect('source-read', IntegrationEnricher())
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
