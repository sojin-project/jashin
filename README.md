# jashin

Assorted Python utilities.


## jashin.dictattr module

Encapsulate deeply nested dict with class.


```python
from jashin.dictattr import DictAttr
from dateutil.parser import parse as dateparse

class User:
    name = DictAttr()
    age = DictAttr()
    created = DictAttr(dateparse) # convert string into datetime object

    def __init__(self, rec):
        self._rec = rec

    def __dictattr__(self):
        """Called by `DictAttr` object to get dictonary."""

        return self._rec

record = {
    "name": "test user",
    "age": 20,
    "created": '2011-01-01T00:00:00'
}

user = User(record)

print(user.name) # -> "test user"
print(user.age)  # -> 20
print(repr(user.created)) # -> datetime.datetime(2011, 1, 1, 0, 0)

user.age = 30
print(record['age']) # -> 30
```

Although `DictAttr` works any classes with `__dictattr__` method, `DictModel` class is provied to avoid boilerplate code.

The `DictAttr` can be used with nested dict object.

```python
from jashin.dictattr import DictAttr, DictAttrList, DictModel
from dateutil.parser import parse as dateparse

class User(DictModel):
    name = DictAttr()
    age = DictAttr()

class Group(DictModel):
    owner = DictAttr(User)
    members = DictAttrList(User)

record = {
    "owner": {
        "name": "owner name",
        "age": 30
    },
    "members": [{
        "name": "member1",
        "age": 30
    },]
}

group = Group(record)

print(group.owner.name) # -> "owner name"
print(group.members[0].name) # -> "member1"
```

Type annotation is supported.

```python
from dateutil.parser import parse as dateparse

class User(DictModel):
    name = DictAttr[str]()  # Explicity specify type
    age = DictAttr(int)     # Inferred from `int` function.
    created = DictAttr(dateparse) # Inferred from `dateparse` function.


user.name = "name"  # OK
user.age = "30"     # Incompatible types in assignment
                    # (expression has type "str", variable has type "int")

user.age = 100      # Incompatible types in assignment
                    # (expression has type "int", variable has type "datetime")

```


## jashin.elapsed module

The `jashin.elapsed` measures elapsed time of arbitrary sections.

Sections can be specified by `with` block.

```python
>>> from jashin.elapsed import Elapsed
>>> e = Elapsed()
>>> def test():
...     a = 1
...     for i in range(10):
...         with e("section 1"):
...             a += 1
...
...         with e("section 2"):
...             a += 1
...
>>> test()
>>> e.print()
section 1: n:10 sum:0.00002 ave:0.00000
section 2: n:10 sum:0.00002 ave:0.00000
```


Or by pair of `begin(name)` and `end()` methods.

```python
>>> from jashin.elapsed import Elapsed
>>> e = Elapsed()
>>> def test2():
...     a = 1
...     for i in range(10):
...         e.begin("section A"):
...         a += 1
...         e.end()
...
...         e.begin("section B"):
...         a += 1
...         e.end()
...
>>> test2()
>>> e.print()
section A: n:10 sum:0.00002 ave:0.00000
section B: n:10 sum:0.00002 ave:0.00000
```


## jashin.jsondefault module

To serialize arbitrary object into JSON, you should define `default` function.

```python

def converter(obj):
    if isinstance(obj, set):
        return list[obj]

    if isinstance(obj, datetime):
        return obj.isoformat()

    ...

print(json.dumps(obj, default=converter))
```

This is tedious. The `jashin.jsondefault.common` provides common functionary to make popular types of objects JSON serializable.

```python

from jashin import jsondefault

repo = jsondefault.common()
print(json.dumps(obj, default=repo)
```

Since `jashin.jsondefault.common` is a [single-dispatch generic function](https://docs.python.org/3/library/functools.html#functools.singledispatch), you can extend it to convert your custom objects.

```python

from jashin import jsondefault

@dataclass
def Foo:
    attr1:int = 100

repo = jsondefault.common()

@repo.register(Foo)
def conv_foo(obj):
    return {'attr1': obj.foo}

print(json.dumps(object, default=repo)
```
