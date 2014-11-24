.. index::
    single: SqliteList

.. _SqliteList:
    
==========
SqliteList
==========
    
This class implements a list backed by an sqlite database.

.. code:: python

    from sqlite_object import SqliteList
    
Supported list behavior
-----------------------

- **list[index]**
    Indexing:
    Read, overwrite, increment operations all work as with an ordinary python list.
    
- **for item in list:**
    Iterating:
    SqliteList objects can be iterated over just like a normal list.  Iterating over the list will lock the list so nothing else can use it.
    
-  **list[0:12], list[1:30:2]**
    Slicing: 
    SqliteLists can be sliced just like normal lists, except that slices return an iterator over the slice.
    Use caution when slicing in a multithreaded situation, the generator returned by a slice **does not** lock the list.
    For many applications, iterating over the whole list may be more efficient than slicing.
    
    
- **len(list)**
    len() works as normal, returning the size of the list.
    

    

Other functions
---------------

.. py:function:: SqliteList(init_list = [], filename=None, coder=json.dumps, decoder=json.loads, index=True, persist=False, commit_every=0)

    Create an sql-backed list.
    
    By default, this will create a new sqlite database with a random filename in the current working directory.
    
    :param init_list: Initialize the list with an iterable.  The objects in *init_list* will *always* be added to the backing database, regardless of whether the database exists already or not.
    :param filename: If you don't want a randomly generated filename for the sqlite db, specify your filename here.  If the database file already exists, this SqliteList will reflect whatever is already in the database (useful for re-opening persisted databases).  You can use the "filename" parameter to make SqliteList clones that will stay up-to-date with eachother (since they share the same DB).  This is useful in multithreading/multiprocessing situations.  If you do this, you MUST set persist=True, otherwise the backing DB will be deleted every time an SqliteList object is garbage collected.
    :param coder: The serializer to use before inserting things into the database.  All items inserted into the list will first be serialized to a string.  The backing sqlite db uses "TEXT" fields to store data, so any serialization should play nice with sqlite TEXT (i.e. pickle or other binary formats may not work well)
    :param decoder: The deserializer to use when reading items from the database.
    :param index: Whether or not to create indexes in the backing DB.  Indexes make lookups much faster, but will increase the size of the DB, and will probably decrease write performance.
    :param persist: Whether or not to delete the database when the SqliteObject is deleted.  Setting persist=True will permit the database to be re-openend with a new SqliteList at a later date.
    :param commit_every: A hint for the SqliteList to decide how many writes should be between commits.  The default (0) will cause *every* write to immediately commit.  Some types of write actions may commit regardless of this counter.
    :type index: True or False
    
.. py:function:: append(item)
    
    Add an item to the end of the list
    
    :param item: The item to add to the end of the list.
    
.. py:function:: prepend(item)
    
    Add an item to the beginning of the list
    
    :param item: The item to add to the beginning of the list
    
.. py:function:: pop_last():

    Remove the last item from the list and return it.  If the list is empty, this will raise an **IndexError**

.. py:function:: pop_first():

    Remove the first item from the list and return it.  If the list is empty, this will raise an **IndexError**
    
.. py:function:: extend(iterable):

    Add each item from iterable to the end of the list.
    
    :param iterable: an iterable object containing items to be added to the list.
    
.. py:function:: write(file)

    Write the entire set out to a file as a JSON list
    
    :param file: A file object to write to
    
.. py:function:: write_lines(file, coder=json.dumps, separator="\\n")

    Write each item in the set to a file as JSON, one item per line.
    
    :param file: A file object to write to
    :param coder: A function to serialize each object before writing it to file
    :param separator: A string to use as a separator if you don't want newline characters
    
.. py:function:: close():
    
    Explicitly close the database, deleting the database file if persist=False
    
    **You do not need to call close on SqliteObjects, close will be called automatically when the object is cleaned up**

.. py:function:: commit():

    Explicitly commit any unsaved changes to disk.  If commit_every is set to 0 or 1, (the default), this is unnessecary since all writes are automatically committed immediately.
    
.. py:function:: get_filename():

    Return the name of the underlying database file.
    
    
Thread safety
-------------

SqliteList uses python multithreading **RLock** to make the list somewhat threadsafe, but the underlying python sqlite3 library is not itself threadsafe, so your mileage may vary.

If you want to share an SqliteList between threads, it would be safer to create a new SqliteList object in each thread and use the same filename for each SqliteList. sqlite itself uses filesystem locks to ensure database integrity so this type of use would be just fine.

If you are using a SqliteList between multiple threads, some operations may be unpredictable (iteration, read-modify-write actions, etc), so use good judgement and put locks around your code.