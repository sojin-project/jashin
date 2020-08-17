from __future__ import annotations

import json
from base64 import b64decode
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from jashin import jsondefault


@dataclass
class Foo:
    a: int


def test_converter() -> None:

    repo = jsondefault.converter()

    @repo.register
    def test_conv(foo: Foo) -> Dict[str, int]:
        return {"a": foo.a}

    d = Foo(a=1)

    obj = json.loads(json.dumps(d, default=repo))

    assert obj == {"a": 1}


def test_common() -> None:

    repo = jsondefault.common()

    d = {1: 1, 2: 2}
    now = datetime.now()

    data = {"items": d.items(), "now": now, "today": now.date(), "bytes": b"abc"}

    ret = json.loads(json.dumps(data, default=repo))

    assert dict(ret["items"]) == d
    assert ret["now"] == now.isoformat()
    assert ret["today"] == now.date().isoformat()
    assert b64decode(ret["bytes"]) == b"abc"
