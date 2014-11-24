.. index::
    single: SqliteDict

.. _SqliteDict:
    
==========
SqliteDict
==========
    
This class implements a dict backed by an sqlite database.

.. code:: python

    from sqlite_object import SqliteDict
    
Be careful what kind of items you use as keys and how they are serialized in JSON.  If you are using keys that do not serialize deterministically (i.e. unordered containers like dict and map), their behavior in the dict may be unpredictable
(i.e. there could be multiple differently-serialized copies of your keys in the SqliteDict).  If you need to use keys like this, you should define a different coder and decoder.
    
Supported dict behavior
-----------------------

    
- **for item in dict:**
    Iterating:
    Iterate through the keys of the dict.
    
- **len(dict)**
    len() works as normal, returning the size of the dict.
    
- **item in dict**
    Membership testing:
    Test if a key is present in the dict
    Membership testing will be slow for large dicts with indexing turned off (indexing is turned on by default)
    
- **dict[key] = value**
    Idexing:
    SqliteDicts are indexed just like regular python dicts.

- **del dict[key]**
    Deletion:
    Remove key from dict
    

Other functions
---------------

.. py:function:: SqliteList(init_dict = [], filename=None, coder=json.dumps, decoder=json.loads, index=True, persist=False, commit_every=0)

    Create an sql-backed dict.
    
    By default, this will create a new sqlite database with a random filename in the current working directory.
    
    :param init_dict: Initialize the dict with another dict.  The objects in *init_dict* will *always* be added to the backing database, regardless of whether the database exists already or not.
    :param filename: If you don't want a randomly generated filename for the sqlite db, specify your filename here.  If the database file already exists, this SqliteList will reflect whatever is already in the database (useful for re-opening persisted databases).  You can use the "filename" parameter to make SqliteList clones that will stay up-to-date with eachother (since they share the same DB).  This is useful in multithreading/multiprocessing situations.  If you do this, you MUST dict persist=True, otherwise the backing DB will be deleted every time an SqliteList object is garbage collected.
    :param coder: The serializer to use before inserting things into the database.  All items inserted into the dict will first be serialized to a string.  The backing sqlite db uses "TEXT" fields to store data, so any serialization should play nice with sqlite TEXT (i.e. pickle or other binary formats may not work well)
    :param decoder: The deserializer to use when reading items from the database.
    :param index: Whether or not to create indexes in the backing DB.  Indexes make lookups much faster, but will increase the size of the DB, and will probably decrease write performance.
    :param persist: Whether or not to delete the database when the SqliteObject is deleted.  Setting persist=True will permit the database to be re-openend with a new SqliteList at a later date.
    :param commit_every: A hint for the SqliteList to decide how many writes should be between commits.  The default (0) will cause *every* write to immediately commit.  Some types of write actions may commit regardless of this counter.
    :type index: True or False
    
.. py:function:: clear()
    
    Remove all items from the dict
    
.. py:function:: get(key, default=None)
    
    Retrieve an item from the dict, returning 'default' if the key is not present in the dict.
    
    :param key: The key to retrieve
    :param default: The value to return if the key is not in the dict.
    
.. py:function:: pop(key, default=None)
    
    Remove an item from the dict and return it, returning 'default' if the key is not present in the dict.
    
    :param key: The key to retrieve and remove
    :param default: The value to return if the key is not in the dict.
    
.. py:function:: popitem()
    
    Remove and return a (key, value) tuple from the dict, or rase a **KeyError** if the dict is empty
    
.. py:function:: setdefault(key, default=None)
    
    If key is in the dictionary, return its value. If not, insert key with a value of default and return default. default defaults to None.
    
    :param key: The key to retrieve/set.
    :param default: The value to set if the key is not in the dict.
    
.. py:function:: update(other)

    If other is a list of 2-tupes, treat the the 2-tuples as (key, value) pairs and add them to the dict.
    
    If other is a dict (if it has an "items" function that iterates of 2-tuples), add each item in other to the dict.
    
    :param other: A dictionary or list of key-value pairs to add to the dict.
    
.. py:function:: items()
    
    Return an iterator over the items ( 2-tuple (key, value) pairs) in the dictionary.
    
    **items() may not lock the underlying database, so if modifications to the DB are made during iteration, the behavior of items will be unpredictable**
    
.. py:function:: keys()

    Return an iterator over the keys in the dictionary.
    
    **keys() may not lock the underlying database, so if modifications to the DB are made during iteration, the behavior of items will be unpredictable**
    
.. py:function:: values()

    Return an iterator over the values in the dictionary.
    
    **values() may not lock the underlying database, so if modifications to the DB are made during iteration, the behavior of items will be unpredictable**
    
.. py:function:: write(file)

    Write the dictionary as JSON to a file.
    
    :param file: a file object to write to.
    
.. py:function:: write_lines(self, file, key_coder=json.dumps, value_coder=json.dumps, separator="\\n", key_val_separator="\\t")
    
    Write the dictionary to a file, one item per line, keys and values separated by a tab.
    
    :param file: File to write to
    :param key_coder: Serialization function to use for serializing keys
    :param value_coder: Serialization function to use for serializing values
    :param separator: Optional line separator if you don't want newlines
    :param key_val_separator: Optional separator to go between keys and values if you don't want to use a tab character
    
.. py:function:: close():
    
    Explicitly close the database, deleting the database file if persist=False
    
    **You do not need to call close on SqliteObjects, close will be called automatically when the object is cleaned up**

.. py:function:: commit():

    Explicitly commit any unsaved changes to disk.  If commit_every is dict to 0 or 1, (the default), this is unnessecary since all writes are automatically committed immediately.
    
.. py:function:: get_filename():

    Return the name of the underlying database file.
    
    
Thread safety
-------------

SqliteList uses python multithreading **RLock** to make the dict somewhat threadsafe, but the underlying python sqlite3 library is not itself threadsafe, so your mileage may vary.

If you want to share an SqliteList between threads, it would be safer to create a new SqliteList object in each thread and use the same filename for each SqliteList. sqlite itself uses filesystem locks to ensure database integrity so this type of use would be just fine.

If you are using a SqliteList between multiple threads, some operations may be unpredictable (iteration, read-modify-write actions, etc), so use good judgement and put locks around your code.