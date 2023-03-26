import logging
import sqlite3
from sqlite3 import Error

try:
    logging.info('hehe')
    connection = sqlite3.connect('database.db')
    logging.info("Init database success")
    with open('schema.sql') as f:
        connection.executescript(f.read())
except Error as e:
    logging.info(e)
finally:
    if connection:
        connection.close()


def log():
    print("Init Database")
