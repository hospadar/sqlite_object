.. sqlite_object documentation master file, created by
   sphinx-quickstart on Wed Oct 29 10:26:55 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


sqlite_object
=========================================

**Sqlite Object is a library of python containers backed by sqlite databases**

This library implements a list, set, and dict which behave very similarly to their builtin counterparts, but they store their data in sqlite databases, which permits the data structures to be as big as your disk and still operate with some efficiently.

sqlite_objects can also be easily persisted since their data is always stored to sqlite.

The source code is available at GitHub_.

Module documentation
--------------------

:ref:`SqliteList`: List-like object

:ref:`SqliteSet`: Set-like object

:ref:`SqliteDict`: Dict-like object

Installation and basic usage
-----------------------------
Install with pip:

.. code-block:: none

    sudo pip install sqlite_object

Getting started is easy, create some objects and use them like you would use their in-memory builtin counterparts:

.. code-block:: python

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

Sqlite objects support *almost* all of the functions of their builtin counterparts, but some functions behave slightly differently, and others are left unimplemented for performance reasons.

.. _GitHub: https://github.com/hospadar/sqlite_object


   
   




