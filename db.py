import sqlite3
from flask import g

def db_connect():
    connection = sqlite3.connect('base.db')
    connection.row_factory = sqlite3.Row
    return connection

def get_db():
    if not hasattr(g, 'connection'):
        g.connection= db_connect()
    return g.connection