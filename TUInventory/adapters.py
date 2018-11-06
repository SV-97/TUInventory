
from classes import User
import sqlite3

def user_adapter(user):
    return f"{user.name};{user.password};{user.salt}"
def user_converter(bytestring):
    username, password, salt = bytestring.split(b";")
    return User(username, password, salt)
    
sqlite3.register_adapter(User, user_adapter)
sqlite3.register_converter("USER", user_converter)