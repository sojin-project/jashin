from __future__ import annotations

from typing import Any, Iterable, List
from functools import singledispatch
import datetime
import base64
import collections.abc

__all__ = ["converter", "common"]


def converter() -> Any:
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

    @singledispatch
    def _repogitory(obj: Any) -> None:
        raise TypeError(
            f"Object of type {obj.__class__.__name__} is not JSON serializable"
        )

    return _repogitory


def common() -> Any:
    """A set of common JSON converter.

    - datetime.date/datetime.datetime -> ISO 8601 format(e.g. YYYY-MM-DD).
    - bytes -> Encoded string in BASE64.
    - Iterables(set, generator, dict.keys(), etc,.) -> list.

    ex::
        json.dumps([{1,2,3}, datetime.datetime.now()], default=common)
    """

    repo = converter()

    @repo.register  # type: ignore
    def conv_date(obj: datetime.datetime) -> str:
        return obj.isoformat()

    @repo.register  # type: ignore
    def conv_datetime(obj: datetime.date) -> str:
        return obj.isoformat()

    @repo.register  # type: ignore
    def conv_bytes(obj: bytes) -> str:
        return base64.b64encode(obj).decode("ascii")

    @repo.register(collections.abc.Iterable)  # type: ignore
    def conv_set(obj: Iterable[Any]) -> List[Any]:
        return list(obj)

    return repo
