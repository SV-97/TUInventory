import sqlite3

adapters.

database = "tuinventory.db"
connection_users = sqlite3.connect(database)
cursor = connection_users.cursor()
cursor.execute(\
"""
CREATE TABLE user (

)

""")