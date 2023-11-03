import os
import sys
from contextlib import contextmanager
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Any, Iterator, Sequence, Generator, Optional, List

from .modules import mock_imports


class MockObject:
    """
    Generic object that can be used to mock anything.
    """

    __display_name__ = "MockObject"
    __name__ = ""
    __decorator_args__: tuple[Any, ...] = ()

    def __new__(cls, *args: Any, **_) -> Any:
        if len(args) == 3 and isinstance(args[1], tuple):
            superclass = args[1][-1].__class__
            if superclass is cls:
                # subclassing MockObject
                return _make_subclass(
                    args[0],
                    superclass.__display_name__,
                    superclass=superclass,
                    attributes=args[2],
                )

        return super().__new__(cls)

    def __init__(self, *_, **__) -> None:
        self.__qualname__ = self.__name__

    def __len__(self) -> int:
        """
        Override __len__ so it returns zero.
        """
        return 0

    def __contains__(self, _: str) -> bool:
        """
        Override __contains__ so it always returns False.
        """
        return False

    def __iter__(self) -> Iterator:
        """
        Override __iter__ so it always returns an empty iterator.
        """
        return iter([])

    def __mro_entries__(self, _: tuple) -> tuple:
        """
        Override __mro_entries__ so it always returns a tuple containing the
        class itself.
        """
        return (self.__class__,)

    def __getitem__(self, key: Any) -> "MockObject":
        """
        Override __getitem__ so it always returns a new MockObject.
        """
        return _make_subclass(str(key), self.__display_name__, self.__class__)()

    def __getattr__(self, key: str) -> "MockObject":
        """
        Override __getattr__ so it always returns a new MockObject.
        """
        return _make_subclass(key, self.__display_name__, self.__class__)()

    def __call__(self, *args: Any, **_) -> Any:
        """
        Override __call__ so it always returns a new MockObject.
        """
        call = self.__class__()
        call.__decorator_args__ = args
        return call

    def __repr__(self) -> str:
        """
        Override __repr__ to return the display name.
        """
        return self.__display_name__


def _make_subclass(
    name: str,
    module: str,
    superclass: Any = MockObject,
    attributes: Any = None,
    decorator_args: tuple = (),
) -> Any:
    """
    Utility method that creates a mock subclass on the fly given its
    parameters.
    """
    attrs = {
        "__module__": module,
        "__display_name__": module + "." + name,
        "__name__": name,
        "__decorator_args__": decorator_args,
    }

    attrs.update(attributes or {})
    return type(name, (superclass,), attrs)


# pylint: disable=too-few-public-methods
class MockModule(ModuleType):
    """
    Object that can be used to mock any module.
    """

    __file__ = os.devnull

    def __init__(self, name: str):
        super().__init__(name)
        self.__all__ = []
        self.__path__ = []

    def __getattr__(self, name: str):
        """
        Override __getattr__ so it always returns a new MockObject.
        """
        return _make_subclass(name, self.__name__)()

    def __mro_entries__(self, _: tuple) -> tuple:
        """
        Override __mro_entries__ so it always returns a tuple containing the
        class itself.
        """
        return (self.__class__,)


class MockFinder(MetaPathFinder):
    """A finder for mocking."""

    def __init__(self, modules: Sequence[str]) -> None:  # noqa
        super().__init__()
        self.modules = modules
        self.loader = MockLoader(self)
        self.mocked_modules: List[str] = []

    def find_spec(
        self,
        fullname: str,
        path: Optional[Sequence[Optional[bytes]]] = None,
        target: Optional[ModuleType] = None,
    ) -> Optional[ModuleSpec]:
        for modname in self.modules:
            # check if fullname is (or is a descendant of) one of our targets
            if modname == fullname or fullname.startswith(modname + "."):
                return ModuleSpec(fullname, self.loader)

        return None

    def invalidate_caches(self) -> None:
        """Invalidate mocked modules on sys.modules."""
        for modname in self.mocked_modules:
            sys.modules.pop(modname, None)


class MockLoader(Loader):
    """A loader for mocking."""

    def __init__(self, finder: MockFinder) -> None:
        super().__init__()
        self.finder = finder

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        self.finder.mocked_modules.append(spec.name)
        return MockModule(spec.name)

    def exec_module(self, module: ModuleType) -> None:
        pass  # nothing to do


@contextmanager
def mock(*mods: str) -> Generator[None, None, None]:
    """
    Insert mock modules during context::

    with mock('target.module.name'):
        # mock modules are enabled here
        ...
    """
    finder = None
    try:
        finder = MockFinder(mods)
        sys.meta_path.insert(0, finder)
        yield
    finally:
        if finder:
            sys.meta_path.remove(finder)
            finder.invalidate_caches()


@contextmanager
def auto_mocks():
    """
    Automatically mock all the modules listed in ``mock_imports``.
    """
    with mock(*mock_imports):
        yield


__all__ = [
    "auto_mocks",
    "mock",
]
