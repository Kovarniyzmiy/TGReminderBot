import sqlite3
import os.path
import time

if os.path.exists("database.db") == False:
    connected_database = sqlite3.connect("database.db")
    cursor = connected_database.cursor()
    cursor.execute("""CREATE TABLE users
                      (
                      ID INTEGER,
                      MODE TEXT,
                      username TEXT,
                      name TEXT,
                      chattype TEXT
                      );
                   """)
    cursor.execute("""CREATE TABLE tasks
                      (
                      ID INTEGER PRIMARY KEY AUTOINCREMENT,
                      createdby TEXT,
                      status TEXT,
                      text TEXT,
                      WID TEXT,
                      CID TEXT,
                      year TEXT,
                      month TEXT,
                      day TEXT,
                      hour TEXT,
                      minute TEXT
                      );
                   """)
    connected_database.commit()
else:
    connected_database = sqlite3.connect("database.db")
    cursor = connected_database.cursor()

print('\n\n-----------------------------OK-----------------------------\n')
