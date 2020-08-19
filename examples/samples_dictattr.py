from datetime import date
from typing import Any, Dict

from dateutil.parser import parse as dateparse

from jashin.dictattr import DictModel, ItemAttr, MappingAttr, SequenceAttr


def load_date(s: str) -> date:
    return dateparse(s).date()


def dump_date(d: date) -> str:
    return d.isoformat()


class User(DictModel):
    name = ItemAttr[str]()
    age = ItemAttr[int]()
    registered = ItemAttr(load_date, dump_date)


def simple() -> None:
    userdict = {"name": "test user", "age": 20, "registered": "2000-01-01"}

    user = User(userdict)

    print(repr(user.registered))  # prints "datetime.date(2000, 1, 1)"

    user.registered = date(2999, 1, 1)
    print(
        userdict
    )  # prints {'name': 'test user', 'age': 20, 'registered': '2999-01-01'}


simple()


class Book(DictModel):
    title = ItemAttr[str]()
    author = ItemAttr(User)


def book() -> None:
    bookdict: Dict[str, Any] = {
        "title": "A title of book",
        "author": {"name": "test user", "age": 20,},
    }
    book = Book(bookdict)
    print(book.author.name)  # prints "test user"

    book.author.name = "updated name"
    print(bookdict["author"]["name"])  # prints "updated name"


book()


class Group(DictModel):
    name = ItemAttr[str]()
    members = SequenceAttr(User)


def group() -> None:
    groupdict: Dict[str, Any] = {
        "name": "A group name",
        "members": [{"name": "member1"}, {"name": "member2"}],
    }

    group = Group(groupdict)
    print(group.members[0].name)  # prints "member1"

    newmember = User({"name": "member3"})
    group.members.append(newmember)
    print(groupdict["members"][2])  # prints {'name': 'member3'}


group()


class Team(DictModel):
    name = ItemAttr[str]()
    roles = MappingAttr[str, User](User)


def team() -> None:
    teamdict: Dict[str, Any] = {
        "name": "A Team name",
        "roles": {
            "manager": {"name": "I'm a manager"},
            "member1": {"name": "I'm a member1"},
        },
    }

    team = Team(teamdict)
    print(team.roles["manager"].name)  # prints "I'm a manager"

    newrole = User({"name": "I'm a director"})
    team.roles["director"] = newrole
    print(teamdict["roles"]["director"])  # prints {'name': 'I'm a director'}


team()
