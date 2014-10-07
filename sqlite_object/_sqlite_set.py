

class SqliteOrderedSet:
    __schema = '''CREATE TABLE IF NOT EXISTS set (key TEXT PRIMARY KEY)'''
    __index = '''CREATE INDEX IF NOT EXISTS set_index ON set (key)'''