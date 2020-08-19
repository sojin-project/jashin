

jashin.dictattr - Encapsulate dictionary with class
============================================================================================


``jashin.dictattr`` provides ``ItemAttr`` and ``DictModel`` to define class that wraps dictionary objects.

Usage
-----------------

To wrap a dictionary like this,


.. code-block::

   userdict = {
       "name": "test user",
       "age": 20,
       "registered": "2000-01-01"
   }

you can define a class with ``ItemAttr`` and ``DictModel``.

.. code-block::

   from datetime import date
   from jashin.dictattr import ItemAttr, DictModel
   from dateutil.parser import parse as dateparse

   class User(DictModel):
       name = ItemAttr()
       age = ItemAttr()
       registered = ItemAttr()

   user = User(userdict)

   print(user.name) # prints "test user"


Assignning value to the member updates corresponding item in the source dictionary object.


.. code-block::

   user.age = 30
   print(user.age)          # prints 30
   print(userdict["age"])  # prints 30



You can specify function to convert value from/to the source dictionary.

.. code-block::

   def load_date(s: str) -> date:
       return dateparse(s).date()

   def dump_date(d: date) -> str:
       return d.isoformat()

   class User(DictModel):
       name = ItemAttr()
       age = ItemAttr()
       registered = ItemAttr(load_date, dump_date)

   user = User(userdict)

   print(user.name) # prints "test user"
   print(repr(user.registered))  # prints "datetime.date(2000, 1, 1)"

   # Update registered
   user.registered = date(2999, 1, 1)
   print(userdict) # prints {'name': 'test user', 'age': 20, 'registered': '2999-01-01'}


Type annotation
+++++++++++++++++++++++++++


``ItemAttr`` is `Generic type <https://docs.python.org/3/library/typing.html#typing.Generic>`_ so you can supply type annotations to the attributes.

.. code-block::

   class User(DictModel):
       name = ItemAttr[str]()
       age = ItemAttr[int]()
       registered = ItemAttr(load_date, dump_date)

Type checkers like `Mypy <https://mypy.readthedocs.io/en/stable/>`_ can check usage of the ``User`` object.

Although type is not specified to ``User.registered`` attribute, Mypy can infer the type of the attribute from ``load_date`` function specified as load function.



Nested item
+++++++++++++++++++++++++++

Child item of the source dictionary can be an another item. For example, following dictionary

.. code-block::

   bookdict = {
       "title": "A title of book",
       "author": {
           "name": "test user",
           "age": 20,
       }
   }

can be wrapped like this.

.. code-block::

   class Book(DictModel):
       title = ItemAttr[str]()
       author = ItemAttr(User)


The ``author`` of the source dictionary is mapped to ``User`` class defined above, so we can get name of the author as follows.

.. code-block::

   book = Book(bookdict)
   print(book.author.name) # prints "test user"

Assignment to the nested item also works.

.. code-block::

   book.author.name = "updated name"
   print(bookdict["author"]["name"]) # prints "updard name"


Sequcence of nested child items
++++++++++++++++++++++++++++++++++++++++

Sequence of nested child items are supported with ``SequenceAttr`` class.

.. code-block::

   groupdict = {
       "name": "A group name",
       "members": [
           {"name": "member1"}, {"name": "member2"}
       ]
   }

   class Group(DictModel):
       name = ItemAttr[str]()
       members = SequenceAttr(User)

   group = Group(groupdict)
   print(group.members[0].name) # prints "member1"

   newmember = User({"name": "member3"})
   group.members.append(newmember)
   print(groupdict["members"][2])  # prints {'name': 'member3'}



Mapping of nested child items
++++++++++++++++++++++++++++++++++++++++

Mapping of nested child items are supported with ``MappingAttr`` class.

.. code-block::

   teamdict = {
       "name": "A Team name",
       "roles": {
           "manager": {
               "name": "I'm a manager"
           },
           "member1": {
               "name": "I'm a member1"
           },
       }
   }

   class Team(DictModel):
       name = ItemAttr[str]()
       roles = MappingAttr(User)

   team = Team(teamdict)
   print(team.roles["manager"].name) # prints "I'm a manager"

   newrole = User({"name": "I'm a director"})
   team.roles["director"] = newrole
   print(teamdict["roles"]["director"])  # prints {'name': 'I'm a director'}






Reference
--------------------------------

.. autoclass:: jashin.dictattr.DictModel

   .. automethod:: jashin.dictattr.DictModel.__dictattr_get__


.. autoclass:: jashin.dictattr.ItemAttr

.. autoclass:: jashin.dictattr.SequenceAttr

.. autoclass:: jashin.dictattr.MappingAttr
