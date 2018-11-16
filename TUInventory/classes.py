import hashlib
import re
from secrets import randbits

import sqlalchemy
from sqlalchemy import Boolean, Column, Integer, LargeBinary, String
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm as orm

Base = declarative_base()

engine = sqlalchemy.create_engine("sqlite:///:memory:", echo=False)
# engine = sqlalchemy.create_engine("sqlite:///test.db", echo=False)

class BigInt(sqlalchemy.types.TypeDecorator):
    """SQLAlchemy datatype for dealing with ints that potentially overflow a basic SQL Integer"""
    impl = sqlalchemy.types.Integer
    def process_bind_param(self, value, dialect):
        """Gets called when writing to db"""
        return str(value)
    def process_result_value(self, value, dialect):
        """Gets called when reading from db"""
        return int(value)

class ContextSession():
    """Factory for contextmanagers for Session objects"""
    @classmethod
    def setup(self, engine):
        """"Initialize a ContextSession class
        Args:
            engine (sqlalchemy.engine.base.Engine): Engine that's bound to the sessionmaker
        Example:
            engine = sqlalchemy.create_engine('sqlite:///:memory:')
            CSession = ContextSession(engine)
            with CSession as session:
                session.add(user1)
                session.add(user2)
        """
        class ContextSession():
            _engine = engine
            _Session = orm.sessionmaker(bind=engine)
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
        return ContextSession

class Producer():
    """Represents a producer of articles"""
    _tablename = "producers"
    def __init__(self, name, uid=None):
        self.uid = uid
        self.name = name

class Article():
    """Represents an article"""
    _tablename = "articles"
    def __init__(self, name, producer=None, uid=None):
        self.uid = uid
        self.name = name
        self.producer = producer

class Device():
    """Represents an article"""
    _tablename = "devices"
    def __init__(self, article=None, uid=None):
        self.uid = uid
        self.article = article

class PhoneNumber():
    __tablename__ = "phone_numbers"
    raw_string = Column(String)
    country_code = Column(String)
    area_code = Column(String)
    subscriber_number = Column(String)
    extension = Column(String)
    pattern = r"(((\+\d{1,3})|(0)) ?([1-9]+) )?(\d+ ?)+(-\d+)?"
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
    class NoNumberFoundWarning(Warning):
        def __init__(self, raw_string):
            super().__init__(self)
            self.args[0] = f"Unable to find phone number in raw_string"
            self.args[1] = raw_string
    @staticmethod
    def _whitespacekiller(string):
        """Remove all non-number characters from a string"""
        return re.sub(r"\D", "", string)
    def _extract_country_code(self):
        country_code = self.match.group(2)
        if country_code and "+" in country_code:
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
        extension = "" if not extension else extension
        return self._whitespacekiller(extension)
    def __str__(self):
        """Build string of the telephone number based on DIN 5008
        """
        extension = f"-{self.extension}" if self.extension else ""
        return f"+{self.country_code} {self.area_code} {self.subscriber_number}{extension}"
    def __format__(self, format_spec):
        return f"{str(self):{format_spec}}"
    
class Location(Base):
    """Represents a physical location where a Device or User may be located"""
    __tablename__ = "locations"
    uid = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    # users = orm.relationship("User", backref="location")
    def __init__(self, name="", uid=None):
        self.name = name
        self.uid = uid

class User(Base):
    """Represents a user of the application
    ToDo:
        - Phonenumber relationship(they seem to be working as of now but aren't even in the database(?))
    """
    __tablename__ = "users"
    uid = Column(Integer, primary_key=True)
    e_mail = Column(String, unique=True)
    password = Column(LargeBinary)
    salt = Column(BigInt)
    name = Column(String)
    surname = Column(String)
    is_admin = Column(Boolean)
    location_uid = Column(Integer, sqlalchemy.ForeignKey("locations.uid"))
    location = orm.relationship("Location", backref=orm.backref("users", uselist=False))
    def __init__(self, e_mail, password, name, surname, phone_nr, uid=None, salt=None):
        self.uid = uid
        self.e_mail = e_mail.lower()
        self.salt = salt if salt else randbits(256)
        self.name = name.lower()
        self.surname = surname.lower()
        self.phone_nr = PhoneNumber(phone_nr)
        self.password = self.hash(password)
        self.is_admin = False
    def hash(self, password):
        """Hash a string with pbkdf2
        The salt is XORd with the e_mail to get the final salt
        """
        return hashlib.pbkdf2_hmac(hash_name="sha512", 
            password=password.encode(), 
            salt=str(int.from_bytes(self.e_mail.encode(), byteorder="big") ^ self.salt).encode(), 
            iterations=9600)

class Responsibility(Base):
    """Represents a responsibility a User has for a Device"""
    __tablename__ = "responsibilities"
    device_uid = Column(Integer, primary_key=True)
    user_uid = Column(Integer, primary_key=True)
    location_uid = Column(Integer, primary_key=True)
    
Base.metadata.create_all(bind=engine) # Database initialized
if __name__ == "__main__":
    location1 = Location("Gebäude 23")
    location2 = Location("Büro")
    user1 = User(e_mail="Schokoladenkönig@googlemail.com", password="12345ibimsdaspasswort", name="Schoko", surname="König", phone_nr="123456")
    user2 = User(e_mail="Oladenkönig@googlemail.com", password="12msdassort", name="Schoko", surname="Künig", phone_nr="654321")
    user1.location = location1
    user2.location = location2
    Session = orm.sessionmaker(bind=engine)
    session = Session()

    session.add(user1)
    session.add(user2)
    session.add(location1)
    session.add(location2)

    del user1
    del user2

    try:
        print(user1.name)
    except Exception:
        print("no user1")
    users = session.query(User).all()

    print("printing")
    for user in users:
        print(f"{user.uid:>5}:   {user.e_mail:>40} | {user.phone_nr:<20} | {user.location.name}")

    session.commit()
    session.close()