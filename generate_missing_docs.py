import os
from typing import Iterable, Optional

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.plugins import Plugin
from platypush.utils.manifest import Manifests


def _get_inspect_plugin():
    p = get_plugin('inspect')
    assert p, 'Could not load the `inspect` plugin'
    return p


def get_all_plugins():
    return sorted([mf.component_name for mf in Manifests.by_base_class(Plugin)])


def get_all_backends():
    return sorted([mf.component_name for mf in Manifests.by_base_class(Backend)])


def get_all_events():
    return _get_inspect_plugin().get_all_events().output


def get_all_responses():
    return _get_inspect_plugin().get_all_responses().output


def _generate_components_doc(
    index_name: str,
    package_name: str,
    components: Iterable[str],
    doc_dir: Optional[str] = None,
):
    if not doc_dir:
        doc_dir = index_name

    index_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'docs',
        'source',
        f'{index_name}.rst',
    )
    docs_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'docs',
        'source',
        'platypush',
        doc_dir,
    )

    for comp in components:
        comp_file = os.path.join(docs_dir, comp + '.rst')
        if not os.path.exists(comp_file):
            comp = f'platypush.{package_name}.{comp}'
            header = '``' + '.'.join(comp.split('.')[2:]) + '``'
            divider = '=' * len(header)
            body = f'\n.. automodule:: {comp}\n    :members:\n'
            out = '\n'.join([header, divider, body])

            with open(comp_file, 'w') as f:
                f.write(out)

    with open(index_file, 'w') as f:
        f.write(
            f'''
{index_name.title()}
{''.join(['='] * len(index_name))}

.. toctree::
    :maxdepth: 1
    :caption: {index_name.title()}:

'''
        )

        for comp in components:
            f.write(f'    platypush/{doc_dir}/{comp}.rst\n')

    _cleanup_removed_components_docs(docs_dir, components)


def _cleanup_removed_components_docs(docs_dir: str, components: Iterable[str]):
    new_components = set(components)
    existing_files = {
        os.path.join(root, file)
        for root, _, files in os.walk(docs_dir)
        for file in files
        if file.endswith('.rst')
    }

    files_to_remove = {
        file
        for file in existing_files
        if os.path.basename(file).removesuffix('.rst') not in new_components
    }

    for file in files_to_remove:
        print(f'Removing unlinked component {file}')
        os.unlink(file)


def generate_plugins_doc():
    _generate_components_doc(
        index_name='plugins', package_name='plugins', components=get_all_plugins()
    )


def generate_backends_doc():
    _generate_components_doc(
        index_name='backends',
        package_name='backend',
        components=get_all_backends(),
        doc_dir='backend',
    )


def generate_events_doc():
    _generate_components_doc(
        index_name='events',
        package_name='message.event',
        components=sorted(event for event in get_all_events().keys() if event),
    )


def generate_responses_doc():
    _generate_components_doc(
        index_name='responses',
        package_name='message.response',
        components=sorted(
            response for response in get_all_responses().keys() if response
        ),
    )


def main():
    generate_plugins_doc()
    generate_backends_doc()
    generate_events_doc()
    generate_responses_doc()


if __name__ == '__main__':
    main()


# vim:sw=4:ts=4:et:
