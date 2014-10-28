sqlite_object
=============

Sqlite3-backed basic python objects for large/persistent data.

Sqlite object was created to handle collections big collections of smallish things and avoiding the complexity/slowness of using a remote datastore.  An example might be keeping a list of millions of identifiers on hand and being able to interact with that list as if it were a regular python list (or dict, or set).

sqlite_object implements a python list, set, and dict that are backed by an sqlite db.  This gives pretty speedy access, but allows efficient handling of collections that are awkwardly large to keep in memory.

The library implements _most_ functions of their stock python counterparts.  Some functions behave slightly differently, and some functions are intentionally left unimplemented.

The package is available on pypi: https://pypi.python.org/pypi/sqlite_object
```bash
sudo pip install sqlite_object
```

By default, values are stored in sqlite as JSON, so anything stored in an sqlite_object container should be JSON-izeable.  If you need to use a different serializer, you can specify it when you create the object.

Ordinarily, the Sqlite db backing the object is removed when the object is deleted, but it's possib
