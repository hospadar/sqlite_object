import sqlite3, os, logging

class SqliteObject:
    
    
    
    commit_counter = 0
    
    def is_open(self):
        return self._is_open
    
    def __init__(self, schema, index_command, filename, coder, decoder, index=True, persist=False, commit_every=0):
        self.db = sqlite3.connect(filename)
        self.persist = persist
        self.filename = filename
        self.logger = logging.getLogger(__name__)
        with self._closeable_cursor() as cursor:
            cursor.execute(schema)
            if index:
                cursor.execute(index_command)
            self.db.commit()
        self._is_open = True
        self.coder = coder
        self.decoder = decoder
        self.commit_every = commit_every
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    def close(self):
        self.logger.debug("closing db")
        self._is_open = False
        if self.persist:
            #commit and close, don't delete
            self.db.commit()
            self.db.close()
        else:
            
            #don't bother commiting, just close and delete
            self.db.close()
            try:
                os.remove(self.filename)
            except:
                logger.warn("Unable to remove db file " + self.filename)
                
                
    def __del__(self):
        self.close()
        
    def _do_write(self):
        """
        Check commit counter and do a commit if need be
        """
        self.commit_counter += 1
        if self.commit_counter >= self.commit_every:
            self.db.commit()
            self.commit_counter = 0
           
    class _CloseableCursor(sqlite3.Cursor):
        def __init__(self, *args, **kwargs):
            super(SqliteObject._CloseableCursor, self).__init__(*args, **kwargs)
        
        def __enter__(self):
            return self
        def __exit__(self, x,y,z):
            self.close()
            
    def _closeable_cursor(self):
        cursor = self.db.cursor(self._CloseableCursor)
        return cursor
        
    