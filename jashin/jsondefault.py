from __future__ import annotations

from typing import Any, Iterable, List, TypeVar
import functools
import datetime
import base64
import collections.abc

__all__ = ["converter", "common"]


def converter() -> functools._SingleDispatchCallable[Any]:
    """Generic function integded to be used for default function of json seriarizer.

    Usage::
        repo = jsondefault.converter()

        class Foo:
            pass

        class Bar:
            pass

        @repo.register(Foo)
        def repo(obj):
            '''Foo object converter'''
            return str(obj)

        @repo.register
        def repo(obj:Bar):
            '''Bar object converter'''
            return str(obj)

        json.dumps([Foo(), Bar()], default=repo)
    """

    @functools.singledispatch
    def _repogitory(obj: Any) -> Any:

        raise TypeError(
            f"Object of type {obj.__class__.__name__} is not JSON serializable"
        )

    return _repogitory


T = TypeVar("T")


def common() -> functools._SingleDispatchCallable[Any]:
    """A set of common JSON converter.

    - datetime.date/datetime.datetime -> ISO 8601 format(e.g. YYYY-MM-DD).
    - bytes -> Encoded string in BASE64.
    - Iterables(set, generator, dict.keys(), etc,.) -> list.

    ex::
        json.dumps([{1,2,3}, datetime.datetime.now()], default=common)
    """

    repo = converter()

    @repo.register
    def conv_date(obj: datetime.datetime) -> str:
        return obj.isoformat()

    @repo.register
    def conv_datetime(obj: datetime.date) -> str:
        return obj.isoformat()

    @repo.register
    def conv_bytes(obj: bytes) -> str:
        return base64.b64encode(obj).decode("ascii")

    @repo.register(collections.abc.Iterable)
    def conv_set(obj: collections.abc.Iterable[T]) -> List[T]:
        return list(obj)

    return repo
