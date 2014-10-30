import json, uuid
from ._sqlite_object import SqliteObject

class SqliteSet(SqliteObject):
    __schema = '''CREATE TABLE IF NOT EXISTS set_table (key TEXT PRIMARY KEY)'''
    __index = '''CREATE INDEX IF NOT EXISTS set_index ON set_table (key)'''
    
    
    def __init__(self, init_set = [], filename=None, coder=json.dumps, decoder=json.loads, index=True, persist=False, commit_every=0):
        super(SqliteSet, self).__init__(self.__schema, self.__index, filename or str(uuid.uuid4())+".sqlite3", coder, decoder, index=index, persist=persist, commit_every=commit_every)
        
        for item in init_set:
            self.add(item)
            
    
    def _getlen(self, cursor):
        for row in cursor.execute('''SELECT COUNT(*) FROM set_table'''):
            return row[0]
    
    def _has(self, cursor, item):
        rows = cursor.execute('''SELECT key FROM set_table WHERE key = ?''', (self._coder(item), ))
        if rows.fetchone() != None:
            return True
        else:
            return False
    
    def _remove(self, cursor, item):
        if self._has(cursor, item):
            self._discard(cursor, item)
        else:
            raise KeyError("Item not in set_table")
    
    def _discard(self, cursor, item):
        cursor.execute('''DELETE FROM set_table WHERE key = ?''', (self._coder(item), ))
        
    def _add(self, cursor, item):
        cursor.execute('''INSERT OR IGNORE INTO set_table (key) VALUES (?)''', (self._coder(item), ))
    
    def __len__(self):
        with self.lock:
            with self._closeable_cursor() as cursor:
                return self._getlen(cursor)
    
    def __contains__(self, item):
        with self.lock:
            with self._closeable_cursor() as cursor:
                return self._has(cursor, item)
            
    def __iter__(self):
        with self.lock:
            with self._closeable_cursor() as cursor:
                for row in cursor.execute('''SELECT key FROM set_table'''):
                    yield self._decoder(row[0])
                
    def add(self, item):
        with self.lock:
            with self._closeable_cursor() as cursor:
                self._add(cursor, item)
            self._do_write()
    
    def remove(self, item):
        with self.lock:
            with self._closeable_cursor() as cursor:
                self._remove(cursor, item)
            self._do_write()
                
    def discard(self, item):
        with self.lock:
            with self._closeable_cursor() as cursor:
                self._discard(cursor, item)
            self._do_write()
        
    def pop(self):
        out = None
        with self.lock:
            with self._closeable_cursor() as cursor:
                rows = cursor.execute('''SELECT key FROM set_table LIMIT 1''')
                row = rows.fetchone()
                if row == None:
                    raise KeyError("Tried to pop empty set_table")
                self._discard(cursor, self._decoder(row[0]))
                out = self._decoder(row[0])
            self._do_write()
            return out
            
    
    def isdisjoint(self, other):
        for item in self:
            if item in other:
                return False
        return True
    
    def issubset(self, other):
        for item in self:
            if item not in other:
                return False
        return True

    def __le__(self, other):
        return self.issubset(other)
    
    def __lt__(self, other):
        return self.issubset(other) and (len(self) < len(other))
    
    def issuperset(self, other):
        for item in other:
            if item not in self:
                return False
        return True
    
    def __ge__(self, other):
        return self.issuperset(other)
    
    def __gt__(self, other):
        return self.issuperset(other) and (len(self) > len(other))
    
    def __eq__(self, other):
        if len(self) == len(other):
            for item in self:
                if item not in other:
                    return False
            return True
        else:
            return False
    
    def update(self, other):
        for item in other:
            self.add(item)
    
    def clear(self):
        with self.lock:
            with self._closeable_cursor() as cursor:
                cursor.execute('''DELETE FROM set_table''')
    