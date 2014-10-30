sqlite_object
=============

Sqlite3-backed basic python objects for large/persistent data.  Works with python 2 (tested with 2.7) and 3

Sqlite object was created to handle collections big collections of smallish things and avoiding the complexity/slowness of using a remote datastore.  An example might be keeping a list of millions of identifiers on hand and being able to interact with that list as if it were a regular python list (or dict, or set).

sqlite_object implements a python list, set, and dict that are backed by an sqlite db.  This gives pretty speedy access, but allows efficient handling of collections that are awkwardly large to keep in memory.

The library implements _most_ functions of their stock python counterparts.  Some functions behave slightly differently, and some functions are intentionally left unimplemented.

The package is available on pypi: https://pypi.python.org/pypi/sqlite_object
```bash
sudo pip install sqlite_object
```

Full package docs here: https://pythonhosted.org/sqlite_object/

The objects are pretty easy to use, and generally behave like their in-memory counterparts.  The unit tests (test_objects.py) contain more in-depth examples.
```python
from sqlite_object import SqliteDict, SqliteList, SqliteSet

#Create a dict
d = SqliteDict()
d["key"] = "value"

#Create a list
l = SqliteList()
l.append("something")

#Create a set
s = SqliteSet()
s.add(1)

#Initializers can be used with all the object types
d = SqliteDict({'key':'value'})
l = SqliteList([1, 2, 3])
s = SqliteSet({1, 2, 3})

#If you want to persist the backing database, say so.  
#You can also specify the filename of the database (instead of using a randomly generated name).  
#Handy if you need to put the db somewhere other than the working directory.  
#All of the objects can be created this way.
l = SqliteList([1, 2, 3], filename="/var/something/db/my_awesome_db.sqlite3", persist=True)

#Then if you need to create it later, it will come back with the same data
del l
l2 = SqliteList(filename="/var/something/db/my_awesome_db.sqlite3", persist=True)


```

