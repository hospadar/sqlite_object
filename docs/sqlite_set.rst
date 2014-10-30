.. index::
    single: SqliteSet

.. _SqliteSet:
    
==========
SqliteSet
==========
    
This class implements a set backed by an sqlite database.

.. code:: python

    from sqlite_object import SqliteSet
    
Be careful what kind of items you put into the set and how they are serialized in JSON.  If you are inserting items into the
set that do not serialize deterministically (i.e. unordered containers like set and map), their behavior in the set may be unpredictable
(i.e. there could be multiple differently-serialized copies of your objects in the SqliteSet).  If you need to insert
containers like this into the set, you should define a different coder and decoder.
    
Supported set behavior
-----------------------

    
- **for item in set:**
    Iterating:
    SqliteList objects can be iterated over just like a normal set.  Iterating over the set will lock the set so nothing else can use it.
    
- **len(set)**
    len() works as normal, returning the size of the set.
    
- **item in set**
    Membership testing:
    Membership testing will be slow for large sets with indexing turned off (indexing is turned on by default)
    
- **set <= other_set**
    Subset testing:
    Test if this set is a subset of another set
    
- **set < other_set**
    Proper subset testing:
    Test if this set is a proper subset of another set (i.e. set <= other_set && set != other_set)

- **set >= other_set**
    Superset testing:
    Test if this set is a superset of another set
    
- **set > other_set**
    Proper superset testing:
    Test if this set is a proper superset of another set (i.e. set >= other_set && set != other_set)
    
- **set == other_set**
    Set equality:
    Test equality of this set to another set
    

    

Other functions
---------------

.. py:function:: SqliteList(init_set = [], filename=None, coder=json.dumps, decoder=json.loads, index=True, persist=False, commit_every=0)

    Create an sql-backed set.
    
    By default, this will create a new sqlite database with a random filename in the current working directory.
    
    :param init_set: Initialize the set with an iterable.  The objects in *init_set* will *always* be added to the backing database, regardless of whether the database exists already or not.
    :param filename: If you don't want a randomly generated filename for the sqlite db, specify your filename here.  If the database file already exists, this SqliteList will reflect whatever is already in the database (useful for re-opening persisted databases).  You can use the "filename" parameter to make SqliteList clones that will stay up-to-date with eachother (since they share the same DB).  This is useful in multithreading/multiprocessing situations.  If you do this, you MUST set persist=True, otherwise the backing DB will be deleted every time an SqliteList object is garbage collected.
    :param coder: The serializer to use before inserting things into the database.  All items inserted into the set will first be serialized to a string.  The backing sqlite db uses "TEXT" fields to store data, so any serialization should play nice with sqlite TEXT (i.e. pickle or other binary formats may not work well)
    :param decoder: The deserializer to use when reading items from the database.
    :param index: Whether or not to create indexes in the backing DB.  Indexes make lookups much faster, but will increase the size of the DB, and will probably decrease write performance.
    :param persist: Whether or not to delete the database when the SqliteObject is deleted.  Setting persist=True will permit the database to be re-openend with a new SqliteList at a later date.
    :param commit_every: A hint for the SqliteList to decide how many writes should be between commits.  The default (0) will cause *every* write to immediately commit.  Some types of write actions may commit regardless of this counter.
    :type index: True or False
    
.. py:function:: add(item)
    
    Add an item to the set.  If the item is already in the set, nothing happens
    
    :param item: The item to add to the set.
    
.. py:function:: remove(item)
    
    Remove an item from the set, if the item does not exist in the set, raise a **KeyError**
    
    :param item: The item to remove from the set.
    
.. py:function:: discard(item)

    Remove an item from the set, if the item does not exist in the set, nothing happens.
    
    :param item: The item to remove from the set.
    
.. py:function:: pop()
    
    Remove an item from the set and return it.  If the set is empty, raise a **KeyError**
    
.. py:function:: isdisjoin(other)

    Test if this set is disjoint from other (i.e. if the intersection of this set and other is an empty set).
    
    :param other: Another set to test.
    
.. py:function:: issubset(other)

    Test if this set is a subset of other.  This is also accessible through the <= operator, i.e. **set <= other**
    
    :param other: Another set to test.
    
.. py:function:: issuperset(other)

    Test if this set is a superset of other.  This is also accessible through the >= operator, i.e. **set >= other**
    
    :param other: Another set to test.
    
.. py:function:: update(iterable)

    Add each item from iterable to the set.
    
    :param iterable: An iterable of items to add to the set.
    
.. py:function:: close():
    
    Explicitly close the database, deleting the database file if persist=False
    
    **You do not need to call close on SqliteObjects, close will be called automatically when the object is cleaned up**

.. py:function:: commit():

    Explicitly commit any unsaved changes to disk.  If commit_every is set to 0 or 1, (the default), this is unnessecary since all writes are automatically committed immediately.
    
.. py:function:: get_filename():

    Return the name of the underlying database file.
    
    
Thread safety
-------------

SqliteList uses python multithreading **RLock** to make the set somewhat threadsafe, but the underlying python sqlite3 library is not itself threadsafe, so your mileage may vary.

If you want to share an SqliteList between threads, it would be safer to create a new SqliteList object in each thread and use the same filename for each SqliteList. sqlite itself uses filesystem locks to ensure database integrity so this type of use would be just fine.

If you are using a SqliteList between multiple threads, some operations may be unpredictable (iteration, read-modify-write actions, etc), so use good judgement and put locks around your code.