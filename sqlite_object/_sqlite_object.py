import sqlite3, os

from threading import RLock

class SqliteObject(object):
    
    _commit_counter = 0
    lock = RLock()
    
    def is_open(self):
        return self._is_open
    
    def __init__(self, schema, index_command, filename, coder, decoder, index=True, persist=False, commit_every=0):
        self._db = sqlite3.connect(filename)
        self._persist = persist
        self._filename = filename
        with self.lock:
            with self._closeable_cursor() as cursor:
                cursor.execute(schema)
                if index:
                    cursor.execute(index_command)
                self._db.commit()
        self._is_open = True
        self._coder = coder
        self._decoder = decoder
        self._commit_every = commit_every
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    def close(self):
        with self.lock:
            self._is_open = False
            if self._persist:
                #commit and close, don't delete
                self._db.commit()
                self._db.close()
            else:
                #don't bother commiting, just close and delete
                self._db.close()
                try:
                    os.remove(self._filename)
                except:
                    pass
                
    def commit(self):
        with self.lock:
            self._db.commit()
    
    def __del__(self):
        self.close()
        
    def _do_write(self):
        """
        Check commit counter and do a commit if need be
        """
        with self.lock:
            self._commit_counter += 1
            if self._commit_counter >= self._commit_every:
                self._db.commit()
                self._commit_counter = 0
           
    class _CloseableCursor(sqlite3.Cursor):
        def __init__(self, *args, **kwargs):
            super(SqliteObject._CloseableCursor, self).__init__(*args, **kwargs)
        
        def __enter__(self):
            return self
        def __exit__(self, x,y,z):
            self.close()
            
    def _closeable_cursor(self):
        with self.lock:
            cursor = self._db.cursor(self._CloseableCursor)
            return cursor
        
    def get_filename(self):
        return self._filename