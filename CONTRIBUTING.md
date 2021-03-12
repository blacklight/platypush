Thanks for considering contributing your work to make Platypush a better product!

Contributions are more than welcome, and the follow the standard Gitlab procedure:

- [Fork the repo](https://git.platypush.tech/platypush/platypush).
- Prepare your changes.
- [Submit a merge request](https://git.platypush.tech/platypush/platypush/-/merge_requests).

Guidelines:

- The code should ideally have no LINT warnings/issues.

- Project conventions:
  - 4 spaces to indent.
  - RST format for classes and methods documentation 
  - Run `python generate_missing_docs.py` if you are adding new plugins/backends to automatically
    generate the doc templates. Make sure that you don't accidentally remove lines elements from
    the docs because of missing dependencies on the machine you use to generate the docs.
  - Naming conventions: plugin classes are named `<Module>Plugin` and backend classes are
    named `<Module>Backend`, with `<Module>` being the (camel-case) representation of the
    Python module of the plugin without the prefix - for example, the plugin under
    `platypush.plugins.light.hue` must be named `LightHuePlugin`.

- If possible, [add a test](https://git.platypush.tech/platypush/platypush/-/tree/master/tests)
  for the new functionality. If you have built a new functionality that works with some specific
  device or service then it's not required to write a test that mocks the whole service, but if
  you are changing some of the core entities (e.g. requests, events, procedures, hooks, crons
  or the bus) then make sure to add tests and not to break the existing tests.

- If the feature requires an optional dependency then make sure to document it:

  - In the class docstring (see other plugins and backends for examples)
  - In [`setup.py`](https://git.platypush.tech/platypush/platypush/-/blob/master/setup.py#L72) as
    an `extras_require` entry
  - In [`requirements.txt`](https://git.platypush.tech/platypush/platypush/-/blob/master/requirements.txt) -
    if the feature is optional then leave it commented and add a one-line comment to explain which
    plugin or backend requires it.
