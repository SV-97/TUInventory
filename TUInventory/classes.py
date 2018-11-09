import hashlib
import re
from secrets import randbits

import sqlalchemy
from sqlalchemy import Column, Integer, LargeBinary, String
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm as orm

Base = declarative_base()

engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=True)

class BigInt(sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.Integer

    def process_bind_param(self, value, dialect):
        """Gets called when writing to db
        """
        return str(value)
    def process_result_value(self, value, dialect):
        """Gets called when reading from db
        """
        return int(value)

class ContextSession():
    """ContextManager for Session objects
    """
    _engine = None
    _Session = None
    def setup(self, engine):
        self._engine = engine
        self._Session = orm.sessionmaker(bind=engine)
    def __enter__(self):
        self.session = self._Session()
        return self.session
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value or exc_type or traceback:
            self.session.rollback()
            return False
        else:
            self.session.commit()
            self.session.close()
            return True


class User(Base):
    __tablename__ = "users"
    uid = Column(Integer, primary_key=True)
    e_mail = Column(String, unique=True)
    password = Column(LargeBinary)
    salt = Column(BigInt)
    name = Column(String)
    surname = Column(String)
    location = Column(Integer)
    phone_nr = Column(String)
    def __init__(self, e_mail, password, name, surname, location, phone_nr, uid=None, salt=None):
        self.uid = uid
        self.e_mail = e_mail.lower()
        self.salt = salt if salt else randbits(256)
        self.name = name.lower()
        self.surname = surname.lower()
        self.location = location
        self.phone_nr = self._normalize_phone_nr(phone_nr)
        self.password = self.hash(password)
    def hash(self, password):
        return hashlib.pbkdf2_hmac(hash_name="sha512", 
            password=password.encode(), 
            salt=str(int.from_bytes(self.e_mail.encode(), byteorder="big") ^ self.salt).encode(), 
            iterations=9600)
    @staticmethod
    def _normalize_phone_nr(input):
        re.match(r"[0-9+49]", input)
        normalized = None
        return normalized

class Location(Base):
    __tablename__ = "locations"
    uid = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    
class Responsibility(Base):
    __tablename__ = "responsibilities"
    device_uid = Column(Integer, primary_key=True)
    user_uid = Column(Integer, primary_key=True)
    location_uid = Column(Integer, primary_key=True)
    
class PhoneNumber():
    def __init__(self, raw_string):
        """Get a Phone Number from raw input string
        Args:
            raw_string (str): String that holds the number
        To do:
            config to set locale (subscriber number prefix and country code)
        """
        self.raw_string = raw_string
        self.match = re.match(self.pattern, self.raw_string)
        if not self.match:
            raise self.NoNumberFoundWarning(self.raw_string)
        self.country_code = self._extract_country_code()
        self.area_code = self._extract_area_code()
        self.subscriber_number = self._extract_subscriber_number()
        self.extension = self._extract_extension()
    pattern = r"(((\+\d{1,3})|(0)) ?([1-9]+) )?(\d+ ?)+(-\d+)?"
    class NoNumberFoundWarning(Warning):
        def __init__(self, raw_string):
            super().__init__(self)
            self.args[0] = f"Unable to find phone number in raw_string"
            self.args[1] = raw_string
    @staticmethod
    def _whitespacekiller(string):
        return re.sub(r"\D", "", string)
    def _extract_country_code(self):
        country_code = self.match.group(2)
        if "+" in country_code:
            return self._whitespacekiller(country_code)
        else:
            return "049"
    def _extract_area_code(self):
        area_code = self.match.group(5) if self.match.group(5) else "9321"
        return self._whitespacekiller(area_code)
    def _extract_subscriber_number(self):
        subscriber_number = self.match.group(6)
        return self._whitespacekiller(subscriber_number)
    def _extract_extension(self):
        extension = self.match.group(7)
        return self._whitespacekiller(extension)
    def __str__(self):
        extension = f"-{self.extension}" if self.extension else ""
        return "f+{self.country_code} {self.area_code} {self.subscriber_number}{extension}"

Base.metadata.create_all(bind=engine) # Datenbank initialisiert

user1 = User(e_mail="Schokoladenkönig@googlemail.com", password="12345ibimsdaspasswort", name="Schoko", surname="König", location=5, phone_nr="123456")
user2 = User(e_mail="Oladenkönig@googlemail.com", password="12msdassort", name="Schoko", surname="Künig", location=45, phone_nr="654321")

Session = orm.sessionmaker(bind=engine)
session = Session()

session.add(user1)
session.add(user2)

users = session.query(User).filter_by(name="Schoko").all()

for user in users:
    print(f"{user.uid:>5}:   {user.e_mail}")
    print(user.salt)
    print(user.salt+1)

session.commit()
session.close()

