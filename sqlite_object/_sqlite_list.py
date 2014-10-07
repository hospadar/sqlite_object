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
    
    _len = 0
    _first_index = 0
    
    def __init__(self, filename=str(uuid.uuid4())+".sqlite3", coder=json.dumps, decoder=json.loads, index=True, persist=False, commit_every=0):
        super(SqliteList, self).__init__(self.__schema, self.__index, filename, coder, decoder, index=index, persist=persist, commit_every=commit_every)
        
        #set initial count
        with self._closeable_cursor() as cursor:
            for row in cursor.execute('''SELECT COUNT(*) FROM list'''):
                self._len = row[0]
        
        #find the lowest index
        if self._len > 0:
            with self._closeable_cursor() as cursor:
                for row in cursor.execute('''SELECT MIN(list_index) FROM list'''):
                    self._first_index = row[0]
                
        
        
    def __len__(self):
        return self._len
    
    
    def __getitem__(self, key):
        if type(key) != int:
            if type(key) == slice:
                start = key.start
                stop = key.stop
                step = key.step
                if start < 0:
                    start = self._len + start
                if stop < 0:
                    stop = self._len + stop
                if step == None:
                    step == 1
                return (self[i] for i in range(start, stop, step))
            else:
                raise TypeError("Key should be int, got " + str(type(key)))
        elif key >= self._len:
            raise IndexError("Sequence index out of range.")
        else:
            with self._closeable_cursor() as cursor:
                if key < 0:
                    key = self._len + key
                    if key >= self._len:
                        raise IndexError("Sequence index out of range.")
                cursor.execute('''SELECT value FROM list WHERE list_index = ?''', (key + self._first_index, ))
                return self._decoder(cursor.fetchone()[0])
    
    def __setitem__(self, key, value):
        if type(key) != int:
            raise TypeError("Key should be int, got " + str(type(key)))
        if key >= self._len:
            raise IndexError("Sequence index out of range.")
        with self._closeable_cursor() as cursor:
            cursor.execute('''REPLACE INTO list (list_index, value) VALUES (?,?)''', (key + self._first_index, self._coder(value)))
        self._do_write()
        
    def __iter__(self):
        with self._closeable_cursor() as cursor:
            cursor.execute('''SELECT value FROM list ORDER BY list_index ASC''')
            for row in cursor:
                yield self._decoder(row[0])
                
    def __reversed__(self):
        with self._closeable_cursor() as cursor:
            cursor.execute('''SELECT value FROM list ORDER BY list_index DESC''')
            for row in cursor:
                yield self._decoder(row[0])
                
    def __contains__(self, item):
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
        with self._closeable_cursor() as cursor:
            cursor.execute('''INSERT INTO list (list_index, value) VALUES (?, ?)''', (self._first_index + self._len, self._coder(item)) )
            self._len += 1 
        self._do_write()
        
    def prepend(self, item):
        """
        Insert an item at the front of the list
        """
        with self._closeable_cursor() as cursor:
            cursor.execute('''INSERT INTO list (list_index, value) VALUES (?, ?)''', (self._first_index - 1, self._coder(item)) )
            self._len += 1
            self._first_index -= 1
        self._do_write()
            
    
    def pop_last(self):
        if self._len > 0:
            val_to_pop = self[-1]
            with self._closeable_cursor() as cursor:
                cursor.execute('''DELETE FROM list WHERE list_index = ?''', (self._first_index + self._len -1, ) )
                self._len -= 1
            self._do_write()
            return val_to_pop
            
    
    def pop_first(self):
        if self._len > 0:
            val_to_pop = self[0]
            with self._closeable_cursor() as cursor:
                cursor.execute('''DELETE FROM list WHERE list_index = ?''', (self._first_index, ) )
                self._first_index += 1
                self._len -= 1
            self._do_write()
            return val_to_pop
        
    def extend(self, iterable):
        """
        Add each item from iterable to the end of the list
        """
        for item in iterable:
            self.append(item)
            
            
            
            
            
            
            