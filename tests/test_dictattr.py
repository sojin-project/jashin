import enum
from typing import Dict, Any

from jashin.dictattr import *


def test_dictattr() -> None:
    class Test:
        field1 = DictAttr[str]()
        field2 = DictAttr[str](name="field_2")
        field3 = DictAttr[str](default="default_field3")

        def __dictattr__(self) -> Dict[str, Any]:
            return self._dict

        _dict = {
            "field1": "field1_value",
            "field_2": "field2_value",
        }

    d = Test()

    assert d.field1 == "field1_value"
    assert d.field2 == "field2_value"
    assert d.field3 == "default_field3"


def test_getter() -> None:
    class Child(Dictionary):
        field1 = DictAttr(int)

    class Label(enum.Enum):
        A = 100
        B = 200

    class Parent(Dictionary):
        field1 = DictAttr(Child)
        field2 = DictAttr(Label)

    d = Parent({"field1": {"field1": "100", "field2": "200",}, "field2": 200})

    assert isinstance(d.field1, Child)
    assert d.field1.field1 == 100
    assert d.field2 is Label.B


def test_list() -> None:
    class Child(Dictionary):
        field1 = DictAttr[str]()

    class Parent(Dictionary):
        field1 = DictAttrList(Child)

    d = Parent({"field1": [{"field1": "100",}, {"field1": "200",}], "field2": 200})

    assert len(d.field1) == 2
    assert d.field1[0].field1 == "100"
    assert d.field1[1].field1 == "200"


def test_set() -> None:
    class Parent(Dictionary):
        field1 = DictAttr[str]()

    d = Parent({})
    d.field1 = "abc"
    assert d._dict == {"field1": "abc"}

    class Parent2(Dictionary):
        field1 = DictAttr[str](setter=int)

    d2 = Parent2({})
    d2.field1 = "1000"
    assert d2._dict == {"field1": 1000}

    def setter(i: int) -> int:
        return i * 2

    class Parent3(Dictionary):
        field1 = DictAttrList(int, setter=setter)

    d3 = Parent3({})
    d3.field1 = [100, 200]
    assert d3._dict == {"field1": [200, 400]}


def test_del() -> None:
    class Parent(Dictionary):
        field1 = DictAttr[str]()

    d = Parent({"field1": "abc"})
    del d.field1
    assert d._dict == {}
