import sqlite3

connection = sqlite3.connect("test.db")
cursor = connection.cursor()

def insert_user_insecure(name):
    cursor.executescript(f"INSERT INTO users(name) VALUES ({name})")

def insert_user_secure(name):
    cursor.execute("INSERT INTO users(name) VALUES (?)", (name,))

insert_user_insecure(input("Benutzername eingeben:"))