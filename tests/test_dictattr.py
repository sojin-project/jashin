import enum
from typing import Any, Dict

from jashin.dictattr import *


def test_dictattr() -> None:
    class Test:
        field1 = ItemAttr[str]()
        field2 = ItemAttr[str](name="field_2")
        field3 = ItemAttr[str](default="default_field3")

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
        field1 = ItemAttr(int)

    class Label(enum.Enum):
        A = 100
        B = 200

    class Parent(DictModel):
        field1 = ItemAttr(Child)
        field2 = ItemAttr(Label)

    d = Parent({"field1": {"field1": "100", "field2": "200",}, "field2": 200})

    assert isinstance(d.field1, Child)
    assert d.field1.field1 == 100
    assert d.field2 is Label.B


def test_set() -> None:
    class Parent(DictModel):
        field1 = ItemAttr[str]()

    d = Parent({})
    d.field1 = "abc"
    assert d.values == {"field1": "abc"}

    class Parent2(DictModel):
        field1 = ItemAttr[str](dump=int)

    d2 = Parent2({})
    d2.field1 = "1000"
    assert d2.values == {"field1": 1000}

    class Child3(DictModel):
        field31 = ItemAttr[str]()

    class Parent3(DictModel):
        field1 = ItemAttr(Child3)

    d3 = Parent3({"field1": {"field31": "value"}})
    c = Child3({"field31": "value2"})
    d3.field1 = c

    assert d3.field1.field31 == "value2"
    assert d3.values == {"field1": {"field31": "value2"}}


def test_del() -> None:
    class Parent(DictModel):
        field1 = ItemAttr[str]()

    d = Parent({"field1": "abc"})
    del d.field1
    assert d.values == {}


def test_list_get() -> None:
    class Parent1(DictModel):
        field1 = SequenceAttr[int]()

    d = Parent1({"field1": [1, 2]})

    assert len(d.field1) == 2
    assert d.field1[0] == 1
    assert d.field1[1] == 2

    class Child2(DictModel):
        field1 = ItemAttr[str]()

    class Parent2(DictModel):
        field1 = SequenceAttr(Child2)

    d2 = Parent2({"field1": [{"field1": "100",}, {"field1": "200",}]})

    assert len(d2.field1) == 2
    assert d2.field1[0].field1 == "100"
    assert d2.field1[1].field1 == "200"


def test_list_set() -> None:
    class Parent1(DictModel):
        field1 = SequenceAttr[int]()

    d = Parent1({"field1": [1, 2]})
    d.field1 = [3, 4, 5]
    assert len(d.field1) == 3
    assert list(d.field1) == [3, 4, 5]

    d.field1[0] = 100
    assert d.values == {"field1": [100, 4, 5]}

    d.field1[:] = [1]
    assert d.values == {"field1": [1]}

    del d.field1[0]
    assert d.values == {"field1": []}

    class Parent2(DictModel):
        field1 = SequenceAttr[int](dump=lambda v: v * 2)

    d2 = Parent2({"field1": [1, 2]})
    d2.field1 = [3, 4, 5]
    assert len(d2.field1) == 3
    assert list(d2.field1) == [6, 8, 10]

    d2.field1[1] = 10
    assert d2.values == {"field1": [6, 20, 10]}

    class Child3(DictModel):
        field1 = ItemAttr[str]()

    class Parent3(DictModel):
        field1 = SequenceAttr(Child3)

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

    c = Child3({"field1": "600"})
    d3.field1[1] = c

    assert d3.values["field1"][1]["field1"] == "600"

    d3.field1[:] = [c]
    assert d3.values == {"field1": [{"field1": "600"}]}


def test_dict_get() -> None:
    class Parent1(DictModel):
        field1 = MappingAttr[str, int]()

    d = Parent1({"field1": {"k1": 1, "k2": 2}})

    assert len(d.field1) == 2
    assert d.field1["k1"] == 1
    assert d.field1["k2"] == 2

    class Child2(DictModel):
        field1 = ItemAttr[str]()

    class Parent2(DictModel):
        field1 = MappingAttr[int, Child2](Child2)

    d2 = Parent2({"field1": {0: {"field1": "100",}, 1: {"field1": "200",}}})

    assert len(d2.field1) == 2
    assert d2.field1[0].field1 == "100"
    assert d2.field1[1].field1 == "200"


def test_Dict_set() -> None:
    class Parent1(DictModel):
        field1 = MappingAttr[str, int]()

    d = Parent1({"field1": {"k1": 1, "k2": 2}})
    d.field1 = {"k3": 3, "k4": 4, "k5": 5}
    assert len(d.field1) == 3
    assert dict(d.field1) == {"k3": 3, "k4": 4, "k5": 5}
    assert d.field1["k3"] == 3

    class Parent2(DictModel):
        field1 = MappingAttr[str, int](dump=lambda v: v * 2)

    d2 = Parent2({"field1": {"k1": 1, "k2": 2}})
    d2.field1 = {"k3": 3, "k4": 4, "k5": 5}
    assert len(d2.field1) == 3
    assert list(d2.field1.values()) == [6, 8, 10]
    assert d2.field1["k3"] == 6

    class Child3(DictModel):
        field1 = ItemAttr[str]()

    class Parent3(DictModel):
        field1 = MappingAttr[str, Child3](Child3)

    d3 = Parent3({"field1": {"a": {"field1": "100",}, "b": {"field1": "200",}}})

    v = {
        "x": Child3({"field1": "300"}),
        "y": Child3({"field1": "400"}),
        "z": Child3({"field1": "500"}),
    }

    d3.field1 = v
    assert len(d3.field1) == 3
    assert d3.field1["x"].field1 == "300"
    assert d3.field1["y"].field1 == "400"
    assert d3.field1["z"].field1 == "500"

    c = Child3({"field1": "600"})
    d3.field1["1"] = c

    assert d3.values["field1"]["1"]["field1"] == "600"
