from __future__ import annotations

import atexit
import collections
import contextlib
import time
from typing import DefaultDict, Iterator, List, NamedTuple, Optional, Tuple


class _Result(NamedTuple):
    name: str
    n: int
    sum: float
    ave: float


class Elapsed:
    _map: DefaultDict[str, List[float]]
    _stack: List[Tuple[str, float]]

    def __init__(self, onexit: bool = False) -> None:
        self._map = collections.defaultdict(list)
        self._stack = []
        if onexit:
            atexit.register(self.print)

    def begin(self, name: str) -> None:
        self._stack.append((name, time.time()))

    def end(self) -> None:
        name, f = self._stack.pop()
        t = time.time() - f
        rec = self._map[name]
        if not rec:
            rec[:] = (0.0, 0)
        rec[0] += t
        rec[1] += 1

    @contextlib.contextmanager
    def __call__(self, name: str) -> Iterator[Elapsed]:
        self.begin(name)
        yield self
        self.end()

    def result(self, name: str) -> Optional[_Result]:
        if name in self._map:
            total, n = self._map[name]
            mean = total / n
            return _Result(name, int(n), total, mean)
        else:
            return None

    def results(self) -> List[Optional[_Result]]:
        ret = []
        for name in sorted(self._map.keys()):
            ret.append(self.result(name))
        return ret

    def print(self, *names: str) -> None:
        i: Iterator[str]

        if names:
            i = iter(names)
        else:
            i = iter(self._map.keys())

        for name in sorted(i):
            rec = self.result(name)
            if rec:
                self._print(rec)
            else:
                print("`%s` is not execused." % name)

    def _print(self, rec: _Result) -> None:
        print("%s: n:%d sum:%.5f ave:%.5f" % (rec.name, rec.n, rec.sum, rec.ave))
