from ._sqlite_object import SqliteObject
import json, uuid


class SqliteDict(SqliteObject):
    """
    Dict-like object backed by an sqlite db.
    
    Make sure your keys serialize repeatably with whatever serializer you choose to use (the default is json).
    If you use un-ordered sets, the json serializer may sometimes generate different keys, so don't do that!
    
    Supports pretty much everything a regular dict supports:
    - setting values
    - retrieving values
    - checking if dict contains a key
    - iterations 
    - get() and setdefault()
    - update(<another dict or list like [(key, value),]>)
    - pop() and popitem()
    """
    __schema = '''CREATE TABLE IF NOT EXISTS dict (key TEXT PRIMARY KEY, value TEXT)'''
    __index = '''CREATE INDEX IF NOT EXISTS dict_index ON dict (key)'''
    
    
    
    def __init__(self, init_dict={}, filename=None, coder=json.dumps, decoder=json.loads, index=True, persist=False, commit_every=0):
        super(SqliteDict, self).__init__(self.__schema, self.__index, filename or str(uuid.uuid4())+".sqlite3", coder, decoder, index=index, persist=persist, commit_every=commit_every)
        for key, value in init_dict.items():
            self[key] = value
        
    def __len__(self):
        with self.lock:
            with self._closeable_cursor() as cursor:
                for row in cursor.execute('''SELECT COUNT(*) FROM dict'''):
                    return row[0]
    
    def __getitem__(self, key):
        with self.lock:
            if type(key) == slice:
                raise KeyError("Slices not allowed in SqliteDict")
            else:
                with self._closeable_cursor() as cursor:
                    cursor.execute('''SELECT value FROM dict WHERE key = ?''', (self._coder(key), ))
                    row = cursor.fetchone()
                    if row != None:
                        return self._decoder(row[0])
                    else:
                        raise KeyError("Mapping key not found in dict")
    
    def __setitem__(self, key, value):
        with self.lock:
            if type(key) == slice:
                raise KeyError("Slices not allowed in SqliteDict")
            else:
                with self._closeable_cursor() as cursor:
                    cursor.execute('''REPLACE INTO dict (key, value) VALUES (?, ?)''', (self._coder(key), self._coder(value)))
            self._do_write()
                
    def __delitem__(self, key):
        with self.lock:
            if type(key) == slice:
                raise KeyError("Slices not allowed in SqliteDict")
            else:
                with self._closeable_cursor() as cursor:
                    cursor.execute('''DELETE FROM dict WHERE key = ?''', (self._coder(key),) )
            self._do_write()
                
    def __iter__(self):
        with self.lock:
            with self._closeable_cursor() as cursor:
                for row in cursor.execute('''SELECT key FROM dict'''):
                    yield self._decoder(row[0])
                
    def __contains__(self, key):
        with self.lock:
            try:
                val = self[key]
            except KeyError:
                return False
            else:
                return True
        
    def clear(self):
        with self.lock:
            with self._closeable_cursor() as cursor:
                cursor.execute('''DELETE FROM dict''')
            
    def get(self, key, default=None):
        with self.lock:
            try:
                val = self[key]
            except KeyError:
                val = default
            return val
    
    def pop(self, key, default=None):
        with self.lock:
            val = self[key]
            del self[key]
            return val
    
    def popitem(self):
        with self.lock:
            with self._closeable_cursor() as cursor:
                cursor.execute('''SELECT key, value FROM dict LIMIT 1''')
                row = cursor.fetchone()
                if row ==  None:
                    raise KeyError("Dict has no more items to pop")
                else:
                    key = self._decoder(row[0])
                    value = self._decoder(row[1])
                    del self[key]
                    return (key, value)
            self._do_write()
    
    def setdefault(self, key, default=None):
        with self.lock:
            try:
                return self[key]
            except KeyError:
                self[key] = default
                return default
            self._do_write()
        
    def update(self, other=None, **kwargs):
        with self.lock:
            if "items" in dir(other):
                for key, value in other.items():
                    self[key] = value
            else:
                for key, value in other:
                    self[key] = value
            for key, value in kwargs:
                self[key] = value
            
    
    class ItemView(object):
        def __init__(self, sq_dict):
            self._sq_dict = sq_dict
        
        def __contains__(self, item):
            key, value = item
            with self._sq_dict._closeable_cursor() as cursor:
                cursor.execute('''SELECT * FROM dict WHERE key = ? AND value = ?''', (self._sq_dict._coder(key), self._sq_dict._coder(value)))
                val = cursor.fetchone()
                if val == None:
                    return False
                else:
                    return True
            
        def __iter__(self):
            with self._sq_dict._closeable_cursor() as cursor:
                for row in cursor.execute('''SELECT key, value FROM dict'''):
                    yield self._sq_dict._decoder(row[0]), self._sq_dict._decoder(row[1])
                    
    class KeyView(object):
        def __init__(self, sq_dict):
            self._sq_dict = sq_dict
        
        def __contains__(self, key):
            with self._sq_dict._closeable_cursor() as cursor:
                cursor.execute('''SELECT * FROM dict WHERE key = ? ''', (self._sq_dict._coder(key), ))
                val = cursor.fetchone()
                if val == None:
                    return False
                else:
                    return True
            
        def __iter__(self):
            with self._sq_dict._closeable_cursor() as cursor:
                for row in cursor.execute('''SELECT key FROM dict'''):
                    yield self._sq_dict._decoder(row[0])
                    
    class ValueView(object):
        def __init__(self, sq_dict):
            self._sq_dict = sq_dict
        
        def __contains__(self, value):
            with self._sq_dict._closeable_cursor() as cursor:
                cursor.execute('''SELECT * FROM dict WHERE value = ? ''', (self._sq_dict._coder(value), ))
                val = cursor.fetchone()
                if val == None:
                    return False
                else:
                    return True
            
        def __iter__(self):
            with self._sq_dict._closeable_cursor() as cursor:
                for row in cursor.execute('''SELECT value FROM dict'''):
                    yield self._sq_dict._decoder(row[0])
    
    def items(self):
        return self.ItemView(self)
    
    def keys(self):
        return self.KeyView(self)
    
    def values(self):
        return self.ValueView(self)