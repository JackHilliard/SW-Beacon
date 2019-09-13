import sqlite3
from config import conf


class DB:
    connection = None

    def __init__(self):
        self.connect()

    def connect(self):
        self.connection = sqlite3.connect(conf['db'], timeout=10)
        self.connection.row_factory = self.dict_factory

    def dict_factory(self, cursor, row):
        dictionary = {}
        for index, col in enumerate(cursor.description):
            dictionary[col[0]] = row[index]
        return dictionary

    def getConn(self):
        return self.connection
