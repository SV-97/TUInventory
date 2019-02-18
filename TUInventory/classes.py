"""All classes of the database connection reside here
This also handles database initialization
"""

from collections import Counter
import hashlib
import re
from secrets import randbits
from threading import Lock, Thread
from time import sleep, time

import cv2
import sqlalchemy
from sqlalchemy import Boolean, Column, Float, Integer, LargeBinary, String
from sqlalchemy.ext.declarative import declarative_base
from PyQt5.QtGui import QImage, QPixmap

from logger import logger
from utils import absolute_path

orm = sqlalchemy.orm

Base = declarative_base()
if __name__ == "__main__":
    print("")
    if not input("Warning! Do you really want to delete the database and write some example data to it? [y/N]: ") in ("y", "Y"):
        exit()
    print("")
    logger.info("Database cleared! This was authorized via a prompt")
    with open(absolute_path("test.db"), "w") as f:
        f.flush()
engine = sqlalchemy.create_engine(f"sqlite:///{absolute_path('test.db')}", echo=False)
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

        class _StateKeepingSession(orm.session.Session):
            def __init__(self):
                super().__init__(bind=engine)
                self.instances = []

            def add(self, instance, *args):
                self.instances.append(instance)
                super().add(instance, *args)

            def add_all(self, instances):
                self.instances += instances
                super().add_all(instances)

        def __enter__(self):
            self.session = self._StateKeepingSession()
            return self.session

        def __exit__(self, exc_type, exc_value, traceback):
            if exc_value or exc_type or traceback:
                self.session.rollback()
                return False # propagate exceptions upwards
            else:
                self.session.commit()
                # [self.session.refresh(instance) for instance in self.session.instances] if I didn't mess up the map below, this can be deleted
                map(self.session.refresh, self.session.instances)
                self.session.expunge_all()
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
    """Represents a device"""
    __tablename__ = "devices"
    uid = Column(Integer, primary_key=True)
    article_uid = Column(Integer, sqlalchemy.ForeignKey("articles.uid"))
    code = Column(String)
    #name = Column(String) # not currently used
    #location_uid = Column(Integer, sqlalchemy.ForeignKey("locations.uid"))
    responsibilities = orm.relationship("Responsibility", backref="device")
    def __init__(self, code=None, uid=None):
        self.uid = uid
        self.code = code
    
    def __str__(self):
        return f"{self.article.name} mit ID {self.uid}"


class PhoneNumber(Base):
    """Get a Phone Number from raw input string
    PhoneNumber can also be stored in database table

        Args:
            raw_string (str): String that holds the number

        To do:
            - config to set locale (subscriber number prefix and country code)
                probably not possible due to precision limitations of system-locale
    """
    __tablename__ = "phone_numbers"
    uid = Column(Integer, primary_key=True)
    user_uid = Column(Integer, sqlalchemy.ForeignKey("users.uid"))
    raw_string = Column(String)
    country_code = Column(String)
    area_code = Column(String)
    subscriber_number = Column(String)
    extension = Column(String)
    pattern = r"(((\+\d{1,3})|(0)) ?([1-9]+) )?(\d+ ?)+(-\d+)?"
    def __init__(self, raw_string):
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
    """Represents a physical location where a Device or User (or Responsibility) may be located"""
    __tablename__ = "locations"
    uid = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    #devices = orm.relationship("Device", backref=orm.backref("location", uselist=False))
    responsibilities = orm.relationship("Responsibility", backref="location", lazy="immediate")
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
    location = orm.relationship("Location", backref=orm.backref("users", lazy="immediate"), uselist=False, lazy="immediate")
    responsibilities = orm.relationship("Responsibility", backref="user")
    phonenumber = orm.relationship(
        "PhoneNumber", 
        backref=orm.backref(
            "user", 
            cascade="all, delete-orphan", 
            single_parent=True), 
        uselist=False, 
        lazy="immediate")

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
        self.password = hashlib.pbkdf2_hmac(
            hash_name="sha512", 
            password=password.encode(), 
            salt=salt, 
            iterations=9600)

    def __str__(self):
        return f"{self.name} {self.surname}".title()


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
logger.info("Database initialized, tables verified")


class Timeout(Thread):
    """Timer that runs in background and executes a function if it's not refreshed
    Important: This is different from the threading.Timer class in that it can provide
    arguments to a function as well as allows reseting the timer, rather than canceling
    completely. to cancel a Timeout set function to None, the thread will then close itself
    down on the next lifecycle check.

        Args:
            function: function that is executed once time runs out
            timeout: time in seconds after which the timeout executes the function
            args: arguments for function

        Attributes:
            timeout: time in seconds afters which the timer times out
            function: function to be executed once time runs out
            args: arguments for function
            kwargs: keyword arguments for function
            lock: mutex for various attributes
            timed_out: boolean presenting wether the timer timed out
            last_interaction_timestamp: unix timestamp of last refresh/initialization
        
        Properties:
            timer: Shows the time remaining until timeout
    """

    def __init__(self, timeout, function, *args, **kwargs):
        super().__init__(name=f"{self.__class__.__name__}Thread_{camera_id}")
        self.timeout = timeout
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.lock = Lock()
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
        """Start the timer"""
        if self.function is None:
            logger.debug("Timeout thread closed because function was None")
            return
        with self.lock:
            if self.is_reset:
                self.is_reset = False           
            else:
                self.timed_out = True
                self.function(*self.args, **self.kwargs)
                return
            difference_to_timeout = self.timeout - (time() - self.last_interaction_timestamp)
        sleep(difference_to_timeout)
        self.run() 


class VideoStreamUISync(Thread):
    """Class to tie a LazyVideoStream to some canvas in Qt
        Args:
            canvas: canvas has to be able to take pixmaps/implement setPixmap
            videostream: Instance of LazyVideoStream that supplies the frames
            barcodes: Counter that holds all found barcodes USE barcode_lock WHEN ACCESSING!
            barcode_lock: Lock for barcodes
    """
    def __init__(self, canvas, videostream):
        super().__init__(name=f"{self.__class__.__name__}Thread_{id(self)}")
        self.canvas = canvas
        self.videostream = videostream
        self.daemon = True
        self.barcodes = Counter()
        self.barcode_lock = Lock()

    @staticmethod
    def _matrice_to_QPixmap(frame):
        """Convert cv2/numpy matrice to a Qt QPixmap"""
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        image = QImage(frame.data, width, height, 3 * width, QImage.Format_RGB888)
        return QPixmap(image)

    def get_most_common(self):
        """Get barcode with highest occurence"""
        with self.barcode_lock:
            return self.barcodes.most_common(1)[0]

    def reset_counter(self):
        with self.barcode_lock:
            self.barcodes = Counter()

    def run(self):
        """Start synchronization"""
        while True:
            self.videostream.request_queue.put(True)
            frame, found_codes = self.videostream.frame_queue.get()
            pixmap = self._matrice_to_QPixmap(frame)
            self.canvas.setPixmap(pixmap)
            if found_codes:
                self.barcodes.update(found_codes)
            cv2.waitKey(1)


if __name__ == "__main__":
    """Tests"""
    """Timer Test
    import threading
    timeout = Timeout(timeout=10, function=print, args=["timed out"])
    timeout.start()
    reset_thread = threading.Thread(target=lambda: timeout.reset() if input() else None) # function for testing - reset on input
    reset_thread.start()
    t = 0
    delta_t = 1
    t1 = time()
    while not timeout.timed_out:
        print(f"Not timed out yet - {t:.2f} seconds passed")
        print(timeout.timer)
        t += delta_t
        sleep(delta_t)
    print(time() - t1)
    timeout.join()
    reset_thread.join()
    """

    location1 = Location("Gebäude 23")
    location2 = Location("Büro")
    location3 = Location("Lager")
    user1 = User(e_mail="Karl@googlemail.com", password="123", name="Karl", surname="König", phonenumber="123456")
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

    producer1 = Producer("Padcon")
    producer2 = Producer("Intel")
    article1 = Article("Prusa Mk3")
    article2 = Article("Kopierpapier")
    article3 = Article("Laptop 123")
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

    device7 = Device("7")
    device7.article = article2
    device7.location = location1

    device8 = Device("8")
    device8.article = article1
    device8.location = location2

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

    resp7 = Responsibility()
    resp7.user = user1
    resp7.location = location1
    resp7.device = device7

    resp8 = Responsibility()
    resp8.user = user1
    resp8.location = location1
    resp8.device = device8

    Session = orm.sessionmaker(bind=engine)
    session = Session()

    session.add(location1)
    session.add(location2)
    session.add(location3)
    session.add_all([user1, user2, user3, user4, user5, user6])
    session.add_all([producer1, producer2])
    session.add_all([article1, article2, article3, article4])
    session.add_all([device1, device2, device3, device4, device5, device6, device7, device8])
    session.add_all([resp1, resp2, resp3, resp4, resp5, resp6, resp7, resp8])

    print("-"*30)
    print(f"{article1.producer.name} produces the following articles")
    for art in producer1.articles:
        print(f"{' '*5}{art.name}")
        print(f"{' '*10}instances of these articles are:")
        for device in art.devices:
            print(f"{device.code:>20} stored at {device.location.name:<20}")
    print("-"*30)
    
    del user1
    del user2
    del location1
    del location2

    try:
        print(user1.name)
    except Exception:
        print("There's no user1, this is wanted and good")
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
