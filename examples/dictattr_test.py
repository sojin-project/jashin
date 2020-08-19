from datetime import date

from dateutil.parser import parse as dateparse

from jashin.dictattr import DictModel, ItemAttr


def load_date(s: str) -> date:
    return dateparse(s).date()


def dump_date(d: date) -> str:
    return d.isoformat()


class User(DictModel):
    name = ItemAttr[str]()
    age = ItemAttr[int]()
    registered = ItemAttr(load_date, dump_date)


userdict = {"name": "test user", "age": 20, "registered": "2000-01-01"}

user = User(userdict)

print(repr(user.registered))  # prints "datetime.date(2000, 1, 1)"

user.registered = date(2999, 1, 1)
print(userdict)  # prints {'name': 'test user', 'age': 20, 'registered': '2999-01-01'}
