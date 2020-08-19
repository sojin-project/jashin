# jashin

Assorted Python utilities.


## jashin.dictattr module

`jashin.dictattr` provides `ItemAttr` and `DictModel` to define class that wraps dictionary objects.

To wrap a dictionary like this,

```python
userdict = {
    "name": "test user",
    "age": 20
}
```

You can use `ItemAttr` and `DictModel`  as follows.

```python
from jashin.dictattr import ItemAttr, DictModel
from dateutil.parser import parse as dateparse

class User(DictModel):
    name = ItemAttr()
    age = ItemAttr()

user = User(userdict)
print(user.name, user.created)

user.age = 30          # updates userdict
pritn(userdict['age']) # prints 30
```

`ItemAttr` supports nested objects.

```python

companydict = {
    "CEO": {
        name: "A CEO",
        age: "21",
    }
    "COO": {
        name: "A COO",
        age: "31",
    }
}
```

To wrap a dictionary above, you can provide `Company` class.

```python
class Company(DictModel):
    CEO = ItemAttr(User)
    COO = ItemAttr(User)

company = Company(companydict)
print(company.CEO.name)  # prints 'A CEO'
```

`DictModel` class is not mandatory, but is provied to avoid boilerplate code. `ItemAttr` works any classes with `__dictattr_get__` method.


```python
class User:
    name = ItemAttr()
    age = ItemAttr()

    def __init__(self, record):
        self._recdict = record

    def __dictattr_get__(self):
        "Called by ItemAttr object to get dictionary"

        return self._recdict
```


Type annotation is supported.

```python

class User(DictModel):
    name = ItemAttr[str]()  # Explicity specify type
    age = ItemAttr(int)     # Inferred from `int` function.


user.name = "name"  # OK
user.age = "30"     # Incompatible types in assignment
                    # The right hand side expression has type "str",
                    # but 'age' attribute has type "int".
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
