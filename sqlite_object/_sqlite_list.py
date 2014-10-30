from ._sqlite_object import SqliteObject
import json, uuid

"""
from sqlite_object import  SqliteList
l = SqliteList()
l.append("hi")
l.append("another one!")
"""

class SqliteList(SqliteObject):
    """
    List-like object backed by an on-disk SQL db
    
    Supports:
    - Indexing
    - Slicing (fairly efficient, but not insanely so)
    - Overwriting list elements
    - Adding items to either end of the list
    - Removing items from either end of the list
    - Checking if the list contains an item
    - Efficient iteration over the whole list (forward and reversed()) 
    
    Doesn't support:
    - Inserting items into the middle of the list
    - Deleting items from the middle of the list
    """
    
    __schema = '''CREATE TABLE IF NOT EXISTS list (list_index INTEGER PRIMARY KEY, value TEXT)'''
    __index = '''CREATE INDEX IF NOT EXISTS list_value ON list (value)'''
    
    
    def __init__(self, init_list = [], filename=None, coder=json.dumps, decoder=json.loads, index=True, persist=False, commit_every=0):
        super(SqliteList, self).__init__(self.__schema, self.__index, filename or str(uuid.uuid4())+".sqlite3", coder, decoder, index=index, persist=persist, commit_every=commit_every)
        
        for item in init_list:
            self.append(item)
                
        
    def _getlen(self, cursor):
        for row in cursor.execute('''SELECT COUNT(*) FROM list'''):
            return row[0]
    def _getmin(self, cursor):
        for row in cursor.execute('''SELECT MIN(list_index) FROM list'''):
            return row[0]
    def _getmax(self, cursor):
        for row in cursor.execute('''SELECT MAX(list_index) FROM list'''):
            return row[0]
    def _getitem(self, cursor, item):
        for row in cursor.execute('''SELECT value FROM list WHERE list_index = (SELECT MIN(list_index) FROM list) + ?''', (item, )):
            return self._decoder(row[0])
        
    def __len__(self):
        with self.lock:
            with self._closeable_cursor() as cursor:
                return self._getlen(cursor)
    
    def _minindex(self):
        with self.lock:
            #find the lowest index
            with self._closeable_cursor() as cursor:
                for row in cursor.execute('''SELECT MIN(list_index) FROM list'''):
                    return row[0]
            #if there's nothing in the list, return 0
            return 0
        
    def _iterate(self, length, irange):
        for i in irange:
            if i >= 0 and i<length:
                yield self[i]
    
    def __getitem__(self, key):
        with self.lock:
            with self._closeable_cursor() as cursor:
                length = self._getlen(cursor)
            if type(key) != int:
                if type(key) == slice:
                    #start = key.start or (0 if key.step > 0 else max(length, 0))
                    #stop = key.stop or (length if key.step > 0 else 0)
                    #step = key.step or 1
                    #if start < 0:
                    #    start = length + start
                    #if stop < 0:
                    #    stop = length + stop
                    ##if step < 0:
                    ##    tmp = start
                    ##    start = max(stop - 1, 0)
                    ##    stop = tmp
                    return (self._iterate(length, range(length)[key.start:key.stop:key.step]))
                else:
                    raise TypeError("Key should be int, got " + str(type(key)))
            elif key >= length:
                raise IndexError("Sequence index out of range.")
            else:
                with self._closeable_cursor() as cursor:
                    
                    if key < 0:
                        key = length + key
                        if key >= length:
                            raise IndexError("Sequence index out of range.")
                        if key < 0:
                            raise IndexError("Sequence index out of range.")
                    cursor.execute('''SELECT value FROM list WHERE list_index = (SELECT MIN(list_index) FROM list) + ?''', (key, ))
                    return self._decoder(cursor.fetchone()[0])
    
    def __setitem__(self, key, value):
        with self.lock:
            if type(key) != int:
                raise TypeError("Key should be int, got " + str(type(key)))
            with self._closeable_cursor() as cursor:
                if key < 0:
                    key = len(self) + key
                    if key < 0:
                        raise IndexError("Sequence index out of range.")
                if key >= len(self):
                    raise IndexError("Sequence index out of range.")
                cursor.execute('''REPLACE INTO list (list_index, value) VALUES ((SELECT MIN(list_index) FROM list) + ?, ?)''', (key, self._coder(value)))
            self._do_write()
        
    def __iter__(self):
        with self.lock:
            with self._closeable_cursor() as cursor:
                cursor.execute('''SELECT value FROM list ORDER BY list_index ASC''')
                for row in cursor:
                    yield self._decoder(row[0])
                
    def __reversed__(self):
        with self.lock:
            with self._closeable_cursor() as cursor:
                cursor.execute('''SELECT value FROM list ORDER BY list_index DESC''')
                for row in cursor:
                    yield self._decoder(row[0])
                
    def __contains__(self, item):
        with self.lock:
            with self._closeable_cursor() as cursor:
                cursor.execute('''SELECT list_index FROM list WHERE value = ?''', (self._coder(value), ))
                if cursor.fetchone() != None:
                    return True
                else:
                    return False
    
    def append(self, item):
        """
        Add an item to the end of the list
        """
        with self.lock:
            with self._closeable_cursor() as cursor:
                cursor.execute('''INSERT INTO list (list_index, value) VALUES ((SELECT MAX(list_index) FROM list) + 1, ?)''', (self._coder(item), ) )
            self._do_write()
        
    def prepend(self, item):
        """
        Insert an item at the front of the list
        """
        with self.lock:
            with self._closeable_cursor() as cursor:
                cursor.execute('''INSERT INTO list (list_index, value) VALUES ((SELECT MIN(list_index) FROM list) - 1, ?)''', ( self._coder(item), ) )
            self._do_write()
            
    
    def pop_last(self):
        with self.lock:
            output = None
            with self._closeable_cursor() as cursor:
                cursor.execute('''BEGIN TRANSACTION''')
                if self._getlen(cursor) < 1:
                    cusror.execute('''END TRANSACTION''')
                    raise IndexError("pop from empty list")
                cursor.execute('''SELECT value FROM list WHERE list_index = (SELECT MAX(list_index) FROM list)''')
                output = self._decoder(cursor.fetchone()[0])
                cursor.execute('''DELETE FROM list WHERE list_index = (SELECT MAX(list_index) FROM list)''')
                self._db.commit()
            self._do_write()
            return output
            
    
    def pop_first(self):
        with self.lock:
            output = None
            with self._closeable_cursor() as cursor:
                cursor.execute('''BEGIN TRANSACTION''')
                if self._getlen(cursor) < 1:
                    cusror.execute('''END TRANSACTION''')
                    raise IndexError("pop from empty list")
                cursor.execute('''SELECT value FROM list WHERE list_index = (SELECT MIN(list_index) FROM list)''')
                output = self._decoder(cursor.fetchone()[0])
                cursor.execute('''DELETE FROM list WHERE list_index = (SELECT MIN(list_index) FROM list)''')
                self._db.commit()
            self._do_write()
            return output
        
    def extend(self, iterable):
        """
        Add each item from iterable to the end of the list
        """
        with self.lock:
            for item in iterable:
                self.append(item)
            
            
    def clear(self):
        with self.lock:
            with self._closeable_cursor() as cursor:
                cursor.execute('''DELETE FROM list''')
            
            
            
            