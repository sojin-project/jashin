from __future__ import annotations

from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    MutableMapping,
    MutableSequence,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

from .omit import OMIT

__all__ = ("ItemAttr", "DictAttr", "MappingAttr", "SequenceAttr", "DictModel")


F = TypeVar("F")
Loader = Callable[[Any], F]
Dumper = Callable[[F], Any]


class DictAttrBase(Generic[F]):
    funcs: Tuple[Optional[Loader[F]], Optional[Dumper[F]]]
    name: Optional[str]
    dict_method: str

    def __init__(
        self,
        func: Optional[Loader[F]] = None,
        *,
        name: Optional[str] = None,
        default: Any = OMIT,
        dumper: Optional[Dumper[F]] = None,
        dict_method: str = "__dictattr_get__",
    ):

        # save loader/dumper as tuple to prevent descr functionary
        self.funcs = (func, dumper)
        self.name = name
        self.default = default
        self.dict_method = dict_method

    def __set_name__(self, owner: Any, name: str) -> None:
        if self.name is None:
            self.name = name

    def _get_dict(self, instance: Any) -> Dict[str, Any]:
        f = getattr(instance, self.dict_method, None)
        if not f:
            raise TypeError(
                f"{instance.__class__.__qualname__} does not provide"
                f"`{self.dict_method}` method."
            )

        return cast(Dict[str, Any], f())

    def _get_value(self, instance: Any, owner: type) -> Tuple[Optional[Loader[F]], Any]:
        """ Get value from dict"""

        data = self._get_dict(instance)

        if self.name not in data:
            if self.default is not OMIT:
                return None, cast(F, self.default)
            raise ValueError(f"{self.name} is not found")

        return self.funcs[0], data[self.name]

    def _dump_value(self, value: Any) -> Any:
        dumper = self.funcs[1]
        if dumper:
            return dumper(value)

        f = getattr(value, self.dict_method, None)
        if f:
            return f()

        return value

    def _set(self, instance: Any, value: Any) -> None:
        assert self.name, "Field name is not provided"
        data = self._get_dict(instance)

        value = self._dump_value(value)
        data[self.name] = value

    def __delete__(self, instance: Any) -> None:
        data = self._get_dict(instance)
        assert self.name, "Field name is not provided"
        del data[self.name]


class ItemAttr(DictAttrBase[F]):
    def __get__(self, instance: Any, owner: type) -> F:
        loader, value = self._get_value(instance, owner)
        if not loader:
            return cast(F, value)

        return loader(value)

    def __set__(self, instance: Any, value: F) -> None:
        assert self.name, "Field name is not provided"
        data = self._get_dict(instance)

        value = self._dump_value(value)
        data[self.name] = value


DictAttr = ItemAttr


_T = TypeVar("_T")


class _SeqAttr(MutableSequence[_T]):
    data: List[Any]
    funcs: Tuple[Optional[Loader[_T]], Optional[Dumper[_T]]]

    def __init__(
        self,
        funcs: Tuple[Optional[Loader[_T]], Optional[Dumper[_T]]],
        data: List[Any],
        dict_method: str,
    ) -> None:
        self.funcs = funcs
        self.data = data
        self.dict_method = dict_method

    def _from_dict(self, o: Any) -> _T:
        loader = self.funcs[0]
        if loader:
            return loader(o)
        else:
            return cast(_T, o)

    def _from_dict_seq(self, o: Iterable[Any]) -> MutableSequence[_T]:
        loader = self.funcs[0]
        if loader:
            return [loader(i) for i in o]
        else:
            return list(o)

    def _to_dict(self, o: _T) -> Any:
        dumper = self.funcs[1]
        if dumper:
            return dumper(o)

        f = getattr(o, self.dict_method, None)
        if f:
            return f()

        return o

    def _to_dict_seq(self, o: Iterable[_T]) -> MutableSequence[_T]:
        dumper = self.funcs[1]
        if dumper:
            return [dumper(i) for i in o]

        ret = []
        for item in o:
            f = getattr(item, self.dict_method, None)
            if f:
                ret.append(f())
            else:
                ret.append(item)

        return ret

    def __len__(self) -> int:
        return len(self.data)

    @overload
    def __getitem__(self, i: int) -> _T:
        ...

    @overload
    def __getitem__(self, i: slice) -> MutableSequence[_T]:
        ...

    def __getitem__(self, i: Union[int, slice]) -> Union[_T, MutableSequence[_T]]:
        if isinstance(i, slice):
            return self._from_dict_seq(self.data[i])
        else:
            return self._from_dict(self.data[i])

    @overload
    def __setitem__(self, i: int, item: _T) -> None:
        ...

    @overload
    def __setitem__(self, i: slice, item: Iterable[_T]) -> None:
        ...

    def __setitem__(self, i: Union[int, slice], item: Union[_T, Iterable[_T]]) -> None:
        if isinstance(i, slice):
            if not isinstance(item, Iterable):
                raise TypeError("can only assign an iterable")
            self.data[i] = self._to_dict_seq(item)
        else:
            self.data[i] = self._to_dict(cast(_T, item))

    def __delitem__(self, i: Union[int, slice]) -> None:
        del self.data[i]

    def __repr__(self) -> str:
        return f"<_AttrList: {self.data!r}>"

    def insert(self, i: int, item: _T) -> None:
        self.data.insert(i, self._to_dict(item))


class SequenceAttr(DictAttrBase[F]):
    def __get__(self, instance: Any, owner: type) -> Sequence[F]:
        _, value = self._get_value(instance, owner)
        return _SeqAttr[F](self.funcs, value, self.dict_method)

    def __set__(self, instance: Any, value: Sequence[F]) -> None:

        assert self.name, "Field name is not provided"
        data = self._get_dict(instance)

        values = [self._dump_value(v) for v in value]
        data[self.name] = values


_K = TypeVar("_K")
_V = TypeVar("_V")


class _MappingAttr(MutableMapping[_K, _V]):
    data: Dict[Any, Any]
    funcs: Tuple[Optional[Loader[_V]], Optional[Dumper[_V]]]

    def __init__(
        self,
        funcs: Tuple[Optional[Loader[_V]], Optional[Dumper[_V]]],
        data: Dict[Any, Any],
        dict_method: str,
    ) -> None:
        self.funcs = funcs
        self.data = data
        self.dict_method = dict_method

    def _from_dict(self, o: Any) -> _V:
        loader = self.funcs[0]
        if loader:
            return loader(o)
        else:
            return cast(_V, o)

    def _to_dict(self, o: _V) -> Any:
        dumper = self.funcs[1]
        if dumper:
            return dumper(o)

        f = getattr(o, self.dict_method, None)
        if f:
            return f()

        return o

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, k: _K) -> _V:
        return self._from_dict(self.data[k])

    def __setitem__(self, k: _K, item: _V) -> None:
        self.data[k] = self._to_dict(item)

    def __delitem__(self, k: _K) -> None:
        del self.data[k]

    def __repr__(self) -> str:
        return f"<_AttrDict: {self.data!r}>"

    def __iter__(self) -> Iterator[_K]:
        return iter(self.data)


K = TypeVar("K")
V = TypeVar("V")


class MappingAttr(Generic[K, V], DictAttrBase[V]):
    def __get__(self, instance: Any, owner: type) -> MutableMapping[K, V]:
        _, value = self._get_value(instance, owner)
        return _MappingAttr[K, V](self.funcs, value, self.dict_method)

    def __set__(self, instance: Any, value: MutableMapping[K, V]) -> None:
        assert self.name, "Field name is not provided"
        data = self._get_dict(instance)

        values = {k: self._dump_value(v) for k, v in value.items()}
        data[self.name] = values


class DictModel:
    values: Dict[str, Any]

    def __init__(self, values: Dict[str, Any]) -> None:
        self.values = values

    def __dictattr_get__(self) -> Dict[str, Any]:
        return self.values
