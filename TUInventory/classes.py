
from secrets import randbits

class User():
    def __init__(self, name, password, salt=randbits(256)):
        self.name = name
        self.password = None
        self.salt = None