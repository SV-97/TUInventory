import hashlib
import re
from secrets import randbits
import threading
from time import sleep, time

import sqlalchemy
from sqlalchemy import Boolean, Column, Float, Integer, LargeBinary, String
from sqlalchemy.ext.declarative import declarative_base

orm = sqlalchemy.orm

Base = declarative_base()
if __name__ == "__main__":
    with open("TUInventory/test.db", "w") as f:
        f.flush()
engine = sqlalchemy.create_engine("sqlite:///TUInventory/test.db", echo=False)
# engine = sqlalchemy.create_engine("sqlite:///:memory:", echo=False)


class BigInt(sqlalchemy.types.TypeDecorator):
    """SQLAlchemy datatype for dealing with ints that potentially overflow a basic SQL Integer"""
    impl = sqlalchemy.types.String
    def process_bind_param(self, value, dialect):
        """Gets called when writing to db"""
        return str(value)

    def process_result_value(self, value, dialect):
        """Gets called when reading from db"""
        return int(value)


def setup_context_session(engine):
    """Factory for contextmanagers for Session objects
    Initialize a ContextSession class
    Args:
        engine (sqlalchemy.engine.base.Engine): Engine that's bound to the sessionmaker
    Example:
        engine = sqlalchemy.create_engine('sqlite:///:memory:')
        CSession = setup_context_session(engine)
        with CSession() as session:
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


class Producer(Base):
    """Represents a producer of articles"""
    __tablename__ = "producers"
    uid = Column(Integer, primary_key=True)
    name = Column(String)
    articles = orm.relationship("Article", backref="producer")
    def __init__(self, name, uid=None):
        self.uid = uid
        self.name = name.title()


class Article(Base):
    """Represents an article"""
    __tablename__ = "articles"
    uid = Column(Integer, primary_key=True)
    name = Column(String)
    producer_uid = Column(Integer, sqlalchemy.ForeignKey("producers.uid"))
    last_price = Column(Float(asdecimal=True))
    devices = orm.relationship("Device", backref="article")
    def __init__(self, name, producer=None, uid=None):
        self.uid = uid
        self.name = name
        self.producer = producer


class Device(Base):
    """Represents an article"""
    __tablename__ = "devices"
    uid = Column(Integer, primary_key=True)
    article_uid = Column(Integer, sqlalchemy.ForeignKey("articles.uid"))
    name = Column(String) # not currently used
    code = Column(String)
    location_uid = Column(Integer, sqlalchemy.ForeignKey("locations.uid"))
    responsibilities = orm.relationship("Responsibility", backref="device")
    def __init__(self, code=None, uid=None):
        self.uid = uid
        self.code = code
    
    def __str__(self):
        return f"{self.article.name} mit ID {self.uid}"


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"
    user_uid = Column(Integer, sqlalchemy.ForeignKey("users.uid"), primary_key=True)
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
        if not self.raw_string:
            self.country_code = ""
            self.area_code = ""
            self.subscriber_number = ""
            self.extension = ""
            self.match = None
            return
        self.match = re.match(self.pattern, self.raw_string)
        if not self.match:
            raise self.NoNumberFoundWarning(raw_string)
        self.country_code = self._extract_country_code()
        self.area_code = self._extract_area_code()
        self.subscriber_number = self._extract_subscriber_number()
        self.extension = self._extract_extension()

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
        """Build string of the telephone number based on DIN 5008"""
        extension = f"-{self.extension}" if self.extension else ""
        return f"+{self.country_code} {self.area_code} {self.subscriber_number}{extension}"

    def __format__(self, format_spec):
        return f"{str(self):{format_spec}}"

    class NoNumberFoundWarning(Warning):
        def __init__(self, raw_string):
            self.raw_string = raw_string
        def __str__(self):
            return f'No telephonenumber was found in: "{self.raw_string}"'


class Location(Base):
    """Represents a physical location where a Device or User may be located"""
    __tablename__ = "locations"
    uid = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    devices = orm.relationship("Device", backref=orm.backref("location", uselist=False))
    responsibilities = orm.relationship("Responsibility", backref="location")
    def __init__(self, name="", uid=None):
        self.name = name.title()
        self.uid = uid

    def __str__(self):
        return self.name


class User(Base):
    """Represents a user of the application"""
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
    responsibilities = orm.relationship("Responsibility", backref="user")
    phonenumber = orm.relationship("PhoneNumber", backref="user", uselist=False)
    def __init__(self, e_mail, password, name="", surname="", phonenumber="", uid=None, salt=None):
        self.uid = uid
        self.e_mail = e_mail.lower()
        self.salt = salt if salt else self.new_salt()
        self.name = name.title()
        self.surname = surname.title()
        if isinstance(phonenumber, PhoneNumber):
            self.phonenumber = phonenumber
        else:
            self.phonenumber = PhoneNumber(phonenumber)
        self.hash(password)
        self.is_admin = False

    @staticmethod
    def new_salt():
        return randbits(256) 

    def hash(self, password):
        """Hash a string with pbkdf2
        The salt is XORd with the e_mail to get the final salt
        """
        salt = str(int.from_bytes(self.e_mail.encode(), byteorder="big") ^ self.salt).encode()
        self.password = hashlib.pbkdf2_hmac(hash_name="sha512", 
            password=password.encode(), 
            salt=salt, 
            iterations=9600)

    def __str__(self):
        return f"{self.name} {self.surname}"


class Responsibility(Base):
    """Represents a responsibility a User has for a Device"""
    __tablename__ = "responsibilities"
    device_uid = Column(Integer, sqlalchemy.ForeignKey("devices.uid"), primary_key=True)
    user_uid = Column(Integer, sqlalchemy.ForeignKey("users.uid"), primary_key=True)
    location_uid = Column(Integer, sqlalchemy.ForeignKey("locations.uid"), primary_key=True)
    def __init__(self, device=None, user=None, location=None):
        self.device = device
        self.user = user
        self.location = location
    def __str__(self):
        return f"{self.user} is responsible for device {self.device} at {self.location}"


Base.metadata.create_all(bind=engine) # Database initialized


class Timeout(threading.Thread):
    def __init__(self, timeout, function, args=None):
        """Timer that runs in background and executes a function if it's not refreshed
        Args:
            function: function that is executed once time runs out
            timeout: time in seconds after which the timeout executes the function
            args: arguments for function
        """
        super().__init__()
        if args is None:
            args = []
        self.timeout = timeout
        self.function = function
        self.args = args
        self.lock = threading.Lock()
        self.timed_out = False
        self.reset()

    def _refresh_timer(self):
        with self.lock:
            return self.timeout - (time() - self.last_interaction_timestamp)

    timer = property(fget=_refresh_timer)

    def reset(self):
        """Reset the internal timer"""
        with self.lock:
            if not self.timed_out:
                self.is_reset = True
                self.last_interaction_timestamp = time()

    def run(self):
        with self.lock:
            if self.is_reset:
                self.is_reset = False           
            else:
                self.timed_out = True
                self.function(*self.args)
                return
            difference_to_timeout = self.timeout - (time() - self.last_interaction_timestamp)
        sleep(difference_to_timeout)
        self.run() 

if __name__ == "__main__":
    """Tests"""
    """ Timer Test
    timeout = Timeout(timeout=10, function=print, args=["timed out"])
    timeout.start()
    reset_thread = threading.Thread(target=lambda: timeout.reset() if input() else None) # function for testing - reset on input
    reset_thread.start()
    t = 0
    delta_t = 1
    while not timeout.timed_out:
        print(f"Not timed out yet - {t:.2f} seconds passed")
        print(timeout.timer)
        t += delta_t
        sleep(delta_t)
    timeout.join()
    reset_thread.join()
    """

    location1 = Location("Gebäude 23")
    location2 = Location("Büro")
    location3 = Location("Lager")
    user1 = User(e_mail="Schokoladenkönig@googlemail.com", password="123", name="Karl", surname="König", phonenumber="123456")
    user2 = User(e_mail="hey@ho.com", password="passwort", name="Bob", surname="Künig", phonenumber="654321")
    user3 = User(e_mail="Mail@mail.com", password="456", name="Bob", surname="Künig", phonenumber="21")
    user4 = User(e_mail="Testo@web.de", password="456", name="testo", surname="Testington", phonenumber="621")
    user5 = User(e_mail="Jack@web.de", password="1234", name="Jack", surname="von Teststadt", phonenumber="+49045 1123")
    user6 = User(e_mail="mymail@gmail.com", password="abc", name="Billy", surname="Bob", phonenumber="651")
    user1.location = location2
    user2.location = location2
    user3.location = location2
    user4.location = location2
    user5.location = location2
    user6.location = location3

    producer1 = Producer("Die Schokoladenfabrik")
    producer2 = Producer("Intel")
    article1 = Article("25kg Schokoblock")
    article2 = Article("Kein 25kg Schokoblock")
    article3 = Article("Das Schokoding")
    article4 = Article("i7 4790k")
    article1.producer = producer1
    article2.producer = producer1
    article3.producer = producer1
    article4.producer = producer2

    device1 = Device("1")
    device1.article = article1
    device1.location = location1

    device2 = Device("2")
    article1.devices.append(device2)
    device2.location = location2

    device3 = Device("3")
    device3.article = article1
    device3.location = location3

    device4 = Device("4")
    device4.article = article4
    device4.location = location3

    device5 = Device("5")
    device5.article = article4
    device5.location = location3

    device6 = Device("6")
    device6.article = article3
    device6.location = location1

    resp1 = Responsibility()
    resp1.user = user1
    resp1.location = location2
    resp1.device = device1

    resp2 = Responsibility()
    resp2.user = user2
    resp2.location = location3
    resp2.device = device2
    
    resp3 = Responsibility()
    resp3.user = user5
    resp3.location = location1
    resp3.device = device3

    resp4 = Responsibility()
    resp4.user = user5
    resp4.location = location1
    resp4.device = device4
    
    resp5 = Responsibility()
    resp5.user = user3
    resp5.location = location2
    resp5.device = device5
    
    resp6 = Responsibility()
    resp6.user = user3
    resp6.location = location1
    resp6.device = device6

    Session = orm.sessionmaker(bind=engine)
    session = Session()

    session.add(location1)
    session.add(location2)
    session.add(location3)
    session.add_all([user1, user2, user3, user4, user5, user6])
    session.add_all([producer1, producer2])
    session.add_all([article1, article2, article3, article4])
    session.add_all([device1, device2, device3, device4, device5, device6])
    session.add_all([resp1, resp2, resp3, resp4, resp5, resp6])

    print("-"*30)
    print(f"{article1.producer.name} hat folgende Artikel")
    for art in producer1.articles:
        print(f"{' '*5}{art.name}")
        print(f"{' '*10}Instanzen dieses Artikels sind:")
        for device in art.devices:
            print(f"{device.code:>20} gelagert in {device.location.name:<20}")
    print("-"*30)
    
    del user1
    del user2
    del location1
    del location2

    try:
        print(user1.name)
    except Exception:
        print("There's no user1")
    print("-"*30)

    users = session.query(User).all()
    locations = session.query()

    for user in users:
        print(f"{user.uid:>5}:   {user.e_mail:>40} | {user.phonenumber:<20} | {user.location.name}")
    print("-"*30)
    print("Known responsibilities for these users are:")
    for user in users:
        for resp in user.responsibilities:
            print(f"{resp.user.name:^15}|{resp.device.code:^15}|{resp.location.name:^15}")
            print(resp.device.article.name)

    session.commit()
    session.close()