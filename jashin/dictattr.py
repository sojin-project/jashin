from __future__ import annotations

from typing import (
    Optional,
    Any,
    Dict,
    cast,
    Sequence,
    TypeVar,
    Generic,
    Callable,
    Tuple,
    Union,
    List
)


from .omit import OMIT

__all__ = ("DictAttr", "DictAttrList", "Dictionary")


F = TypeVar("F")
Getter = Callable[[Any], F]
Setter = Callable[[F], Any]


class DictAttrBase(Generic[F]):
    funcs: Tuple[Optional[Getter[F]], Optional[Setter[F]]]
    name: Optional[str]

    def __init__(
        self,
        func: Optional[Getter[F]] = None,
        *,
        name: Optional[str] = None,
        default: Any = OMIT,
        dict_method: Union[
            str, Callable[[DictAttrBase[F], Any], Dict[str, Any]]
        ] = "__dictattr__",
        setter: Optional[Setter[F]] = None,
    ):

        # save getter/setter as tuple to prevent descr functionary
        self.funcs = (func, setter)
        self.name = name
        self.default = default
        self.dict_method = dict_method

    def __set_name__(self, owner: Any, name: str) -> None:
        if self.name is None:
            self.name = name

    def _get_dict(self, instance: Any) -> Dict[str, Any]:
        if callable(self.dict_method):
            return self.dict_method(self, instance)
        f = getattr(instance, self.dict_method)
        if not f:
            raise TypeError(
                f"{instance.__class__.__qualname__} does not provide"
                f"`{self.dict_method}` method."
            )

        return cast(Dict[str, Any], f())

    def _get_value(self, instance: Any, owner: type) -> Tuple[Optional[Getter[F]], Any]:
        """ Get value from dict"""

        data = self._get_dict(instance)

        if self.name not in data:
            if self.default is not OMIT:
                return None, cast(F, self.default)
            raise ValueError(f"{self.name} is not found")

        return self.funcs[0], data[self.name]

    def _set(self, instance: Any, value: Any) -> None:
        assert self.name, "Field name is not provided"
        data = self._get_dict(instance)
        setter = self.funcs[1]
        if setter:
            v = setter(value)
            data[self.name] = v
        else:
            data[self.name] = value

    def __delete__(self, instance: Any) -> None:
        data = self._get_dict(instance)
        assert self.name, "Field name is not provided"
        del data[self.name]


class DictAttr(DictAttrBase[F]):
    def __get__(self, instance: Any, owner: type) -> F:
        getter, value = self._get_value(instance, owner)
        if not getter:
            return cast(F, value)

        return getter(value)

    def __set__(self, instance: Any, value: F) -> None:
        self._set(instance, value)


class DictAttrList(DictAttrBase[F]):
    def __get__(self, instance: Any, owner: type) -> Sequence[F]:
        getter, value = self._get_value(instance, owner)
        if not getter:
            return cast(Sequence[F], value)

        return [getter(v) for v in value]

    def __set__(self, instance: Any, value: Sequence[F]) -> None:
        assert self.name, "Field name is not provided"

        setter = self.funcs[1]
        values: List[Any]

        data = self._get_dict(instance)

        if setter:
            data[self.name] = [setter(v) for v in value]
        else:
            data[self.name] = value

class Dictionary:
    _dict: Dict[str, Any]

    def __init__(self, dict: Dict[str, Any]) -> None:
        self._dict = dict

    def __dictattr__(self) -> Dict[str, Any]:
        return self._dict
