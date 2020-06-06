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
    List,
    MutableSequence,
    Iterable,
    overload
)

import collections.abc

from .omit import OMIT

__all__ = ("DictAttr", "DictAttrList", "DictModel")


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




_T = TypeVar("_T")
#class UserList(MutableSequence[_T]):
#    data: List[_T]
#    def __init__(self, initlist: Optional[Iterable[_T]] = ...) -> None: ...
#    def __lt__(self, other: object) -> bool: ...
#    def __le__(self, other: object) -> bool: ...
#    def __gt__(self, other: object) -> bool: ...
#    def __ge__(self, other: object) -> bool: ...
#    def __contains__(self, item: object) -> bool: ...
#    def __len__(self) -> int: ...
#    @overload
#    def __getitem__(self, i: int) -> _T: ...
#    @overload
#    def __getitem__(self, i: slice) -> MutableSequence[_T]: ...
#    @overload
#    def __setitem__(self, i: int, o: _T) -> None: ...
#    @overload
#    def __setitem__(self, i: slice, o: Iterable[_T]) -> None: ...
#    def __delitem__(self, i: Union[int, slice]) -> None: ...
#    def __add__(self: _S, other: Iterable[_T]) -> _S: ...
#    def __iadd__(self: _S, other: Iterable[_T]) -> _S: ...
#    def __mul__(self: _S, n: int) -> _S: ...
#    def __imul__(self: _S, n: int) -> _S: ...
#    def append(self, item: _T) -> None: ...
#    def insert(self, i: int, item: _T) -> None: ...
#    def pop(self, i: int = ...) -> _T: ...
#    def remove(self, item: _T) -> None: ...
#    def clear(self) -> None: ...
#    def copy(self: _S) -> _S: ...
#    def count(self, item: _T) -> int: ...
#    def index(self, item: _T, *args: Any) -> int: ...
#    def reverse(self) -> None: ...
#    def sort(self, *args: Any, **kwds: Any) -> None: ...
#    def extend(self, other: Iterable[_T]) -> None: ...

class _AttrList(MutableSequence[_T]):
    data: List[Any]
    funcs: Tuple[Optional[Getter[_T]], Optional[Setter[_T]]]

    def __init__(self, funcs:Tuple[Optional[Getter[_T]], Optional[Setter[_T]]], data:List[Any])->None:
        self.func = funcs
        self.data = data

    def _from_dict(self, o: Any)->_T:
        getter = self.funcs[0]
        if getter:
            return getter(o)
        else:
            return cast(_T, o)

    def _from_dict_seq(self, o: Iterable[Any])->MutableSequence[_T]:
        getter = self.funcs[0]
        if getter:
            return [getter(i) for i in o]
        else:
            return list(o)

    def _to_dict(self, o: _T)->Any:
        setter = self.funcs[1]
        if setter:
            return setter(o)
        else:
            return o

    def _to_dict_seq(self, o: Iterable[_T])->MutableSequence[_T]:
        setter = self.funcs[1]
        if setter:
            return [setter(i) for i in o]
        else:
            return list(o)

    def __len__(self) -> int:
        return len(self.data)

    @overload
    def __getitem__(self, i: int) -> _T: ...

    @overload
    def __getitem__(self, i: slice) -> MutableSequence[_T]: ...

    def __getitem__(self, i:Union[int, slice])->Union[_T, MutableSequence[_T]]:
        if isinstance(i, slice):
            return self._from_dict_seq(self.data[i])
        else:
            return self._from_dict(self.data[i])

    @overload
    def __setitem__(self, i: int, item: _T) -> None: ...

    @overload
    def __setitem__(self, i: slice, item: Iterable[_T]) -> None: ...

    def __setitem__(self, i:Union[int, slice], item:Union[_T, Iterable[_T]])->None:
        if isinstance(i, slice):
            if not isinstance(item, Iterable):
                raise TypeError('can only assign an iterable')
            self.data[i] = self._to_dict_seq(item)
        else:
            self.data[i] = self._to_dict(cast(_T, item))

    def __delitem__(self, i:Union[int, slice])->None:
        del self.data[i]

    def __repr__(self)->str:
        return repr(self.data)

    def append(self, item:_T)->None:
        self.data.append(self._to_dict(item))

    def insert(self, i:int, item:_T)->None:
        self.data.insert(i, self._to_dict(item))

    def extend(self, other:Iterable[_T])->None:
        self.data.extend(self._to_dict_seq(other))




class DictAttrList(DictAttrBase[F]):
    def __get__(self, instance: Any, owner: type) -> Sequence[F]:
        _, value = self._get_value(instance, owner)
        return _AttrList[F](self.funcs, value)

    def __set__(self, instance: Any, value: Sequence[F]) -> None:
        assert self.name, "Field name is not provided"

        setter = self.funcs[1]
        if setter:
            data[self.name] = [setter(v) for v in value]
        else:
            data[self.name] = value


class DictModel:
    _dict: Dict[str, Any]

    def __init__(self, dict: Dict[str, Any]) -> None:
        self._dict = dict

    def __dictattr__(self) -> Dict[str, Any]:
        return self._dict
