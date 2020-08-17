import enum
from typing import Any, Dict

from jashin.dictattr import *


def test_dictattr() -> None:
    class Test:
        field1 = DictAttr[str]()
        field2 = DictAttr[str](name="field_2")
        field3 = DictAttr[str](default="default_field3")

        def __dictattr_get__(self) -> Dict[str, Any]:
            return self._dict

        _dict = {
            "field1": "field1_value",
            "field_2": "field2_value",
        }

    d = Test()

    assert d.field1 == "field1_value"
    assert d.field2 == "field2_value"
    assert d.field3 == "default_field3"


def test_loader() -> None:
    class Child(DictModel):
        field1 = DictAttr(int)

    class Label(enum.Enum):
        A = 100
        B = 200

    class Parent(DictModel):
        field1 = DictAttr(Child)
        field2 = DictAttr(Label)

    d = Parent({"field1": {"field1": "100", "field2": "200",}, "field2": 200})

    assert isinstance(d.field1, Child)
    assert d.field1.field1 == 100
    assert d.field2 is Label.B


def test_set() -> None:
    class Parent(DictModel):
        field1 = DictAttr[str]()

    d = Parent({})
    d.field1 = "abc"
    assert d._dict == {"field1": "abc"}

    class Parent2(DictModel):
        field1 = DictAttr[str](dumper=int)

    d2 = Parent2({})
    d2.field1 = "1000"
    assert d2._dict == {"field1": 1000}

    class Child3(DictModel):
        field31 = DictAttr[str]()

    class Parent3(DictModel):
        field1 = DictAttr(Child3)

    d3 = Parent3({"field1": {"field31": "value"}})
    d3.field1 = Child3({"field31": "value2"})

    assert d3.field1.field31 == "value2"


def test_del() -> None:
    class Parent(DictModel):
        field1 = DictAttr[str]()

    d = Parent({"field1": "abc"})
    del d.field1
    assert d._dict == {}


def test_list_get() -> None:
    class Parent1(DictModel):
        field1 = DictAttrList[int]()

    d = Parent1({"field1": [1, 2]})

    assert len(d.field1) == 2
    assert d.field1[0] == 1
    assert d.field1[1] == 2

    class Child2(DictModel):
        field1 = DictAttr[str]()

    class Parent2(DictModel):
        field1 = DictAttrList(Child2)

    d2 = Parent2({"field1": [{"field1": "100",}, {"field1": "200",}]})

    assert len(d2.field1) == 2
    assert d2.field1[0].field1 == "100"
    assert d2.field1[1].field1 == "200"


def test_list_set() -> None:
    class Parent1(DictModel):
        field1 = DictAttrList[int]()

    d = Parent1({"field1": [1, 2]})
    d.field1 = [3, 4, 5]
    assert len(d.field1) == 3
    assert list(d.field1) == [3, 4, 5]

    class Parent2(DictModel):
        field1 = DictAttrList[int](dumper=lambda v: v * 2)

    d2 = Parent2({"field1": [1, 2]})
    d2.field1 = [3, 4, 5]
    assert len(d2.field1) == 3
    assert list(d2.field1) == [6, 8, 10]

    class Child3(DictModel):
        field1 = DictAttr[str]()

    class Parent3(DictModel):
        field1 = DictAttrList(Child3)

    d3 = Parent3({"field1": [{"field1": "100",}, {"field1": "200",}]})

    seq = [
        Child3({"field1": "300"}),
        Child3({"field1": "400"}),
        Child3({"field1": "500"}),
    ]

    d3.field1 = seq
    assert len(d3.field1) == 3
    assert d3.field1[0].field1 == "300"
    assert d3.field1[1].field1 == "400"
    assert d3.field1[2].field1 == "500"
