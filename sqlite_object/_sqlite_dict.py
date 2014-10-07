


class SqliteDict:
    __schema = '''CREATE TABLE IF NOT EXISTS dict (key TEXT PRIMARY KEY, value TEXT)'''
    __index = '''CREATE INDEX IF NOT EXISTS dict_index ON dict (key)'''