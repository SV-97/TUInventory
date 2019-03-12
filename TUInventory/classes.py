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
from passlib.hash import argon2
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


class IntegrityError(IOError):
    """Error to raise if an operation compromises database integrity"""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'Couldn\'t create instance with given Parameters: "{self.message}"'

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

            def add(self, instance, *args, **kwargs):
                self.instances.append(instance)
                super().add(instance, *args, **kwargs)

            def add_all(self, instances, *args, **kwargs):
                self.instances += instances
                super().add_all(instances, *args, **kwargs)

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
                for x in map(self.session.refresh, self.session.instances):
                    pass # refresh all instances via side effect of map
                self.session.expunge_all()
                self.session.close()
                return True
    return ContextSession


class Producer(Base):
    """Represents a producer of articles"""
    __tablename__ = "producers"
    uid = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    articles = orm.relationship("Article", backref="producer")
    def __init__(self, name, uid=None):
        self.uid = uid
        self.name = name.title()

    def __str__(self):
        return f"{self.uid} {self.name}"


class Article(Base):
    """Represents an article"""
    __tablename__ = "articles"
    uid = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    producer_uid = Column(Integer, sqlalchemy.ForeignKey("producers.uid"))
    #last_price = Column(Float(asdecimal=True))
    devices = orm.relationship(
        "Device", 
        backref=orm.backref("article", lazy="immediate"), 
        lazy="immediate")
    def __init__(self, name, producer=None, uid=None):
        self.uid = uid
        self.name = name
        self.producer = producer

    def __str__(self):
        return f"{self.uid} {self.name}"

class Device(Base):
    """Represents a device"""
    __tablename__ = "devices"
    uid = Column(Integer, primary_key=True)
    article_uid = Column(Integer, sqlalchemy.ForeignKey("articles.uid"))
    code = Column(String)
    responsibility = orm.relationship(
        "Responsibility", 
        backref=orm.backref("device", lazy="immediate", uselist=False), 
        lazy="immediate", 
        uselist=False)
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
    pattern = r"(?P<prelude>(?P<country_code>(?:\+\d{1,3})|(?:0)) *(?P<area_code>(?:[1-9])+) )?(?P<subscriber_number>(?:\d+ ?)+)(?P<extension>[-\+]\d+)?"
    def __init__(self, raw_string):
        self.raw_string = raw_string
        if not self.raw_string:
            self.country_code = ""
            self.area_code = ""
            self.subscriber_number = ""
            self.extension = ""
            self.match = None
            return
        self.match = re.search(self.pattern, self.raw_string)
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
        country_code = self.match.group("country_code")
        if country_code and "+" in country_code:
            return self._whitespacekiller(country_code)
        else:
            return "049"

    def _extract_area_code(self):
        area_code = self.match.group("area_code")
        area_code = "9321" if not area_code else area_code
        return self._whitespacekiller(area_code)

    def _extract_subscriber_number(self):
        subscriber_number = self.match.group("subscriber_number")
        return self._whitespacekiller(subscriber_number)

    def _extract_extension(self):
        extension = self.match.group("extension")
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
    """Represents a physical location where a User (or Responsibility) may be located"""
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
    location = orm.relationship(
        "Location", 
        backref=orm.backref("users", lazy="immediate"), 
        uselist=False, 
        lazy="immediate")
    responsibilities = orm.relationship("Responsibility", backref="user")
    phonenumber = orm.relationship(
        "PhoneNumber", 
        backref=orm.backref("user", cascade="all, delete-orphan", single_parent=True), 
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
        return randbits(128)

    def hash(self, password):
        """Hash a string with argon2
        The salt is concatenated with the e_mail to get the final salt
        """
        salt = f"{self.salt}{self.e_mail}".encode()
        hash = argon2.using(
            salt=salt, 
            rounds=512, 
            memory_cost=1024, 
            max_threads=8, 
            digest_size=256).hash(password)
        self.password = re.match(r"\$argon2i\$v=\d+\$m=\d+,t=\d+,p=\d+\$(?P<hash>.+)", hash).\
            group("hash").encode()

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
    completely. To cancel a Timeout set function to None, the thread will then close itself
    down on the next lifecycle check.

        Args:
            function: function that is executed once time runs out
            timeout: time in seconds after which the timeout executes the function
            args: arguments for function
            kwargs: keyword arguments for function

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
        super().__init__(name=f"{self.__class__.__name__}Thread_{function.__name__}")
        self.daemon = True
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
            signal: qt-signal that's emitted if a barcode has been recognized
            job: set to "both", "codes" or "frames" to set whether it should 
                only process image data, barcodes and signals or both

        Attributes:
            barcodes: Counter that holds all found barcodes USE barcode_lock WHEN ACCESSING!
            barcode_lock: Lock for barcodes
            sensibility: How often a barcode has to be recognized to count it as valid
    """
    def __init__(self, canvas, videostream, signal, job="both"):
        super().__init__(name=f"{self.__class__.__name__}Thread_{id(self)}")
        self.canvas = canvas
        self.videostream = videostream
        self.daemon = True
        self.barcodes = Counter()
        self.barcode_lock = Lock()
        self.sensibility = 10
        self.signal = signal
        self.job = job

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

    def update_counter(self, found_codes):
        with self.barcode_lock:
            self.barcodes.update(found_codes)

    def run(self):
        """Start synchronization"""
        while True:
            self.videostream.request_queue.put(True)
            frame, found_codes = self.videostream.frame_queue.get()
            if self.job == "frames" or self.job == "both":
                pixmap = self._matrice_to_QPixmap(frame)
                self.canvas.setPixmap(pixmap)
            elif self.job == "codes" or self.job == "both":
                if found_codes:
                    self.update_counter(found_codes)
                    most_common = self.get_most_common()
                    if most_common[1] > self.sensibility:
                        self.signal.emit(most_common[0][1])
                        self.reset_counter()
                        sleep(10)
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

    import random
    random.seed(0)
    
    location1 = Location("Gebäude 23")
    location2 = Location("Büro")
    location3 = Location("Lager")
    locations = (
        location1,
        location2,
        location3)


    user1 = User(e_mail="Karl@googlemail.com", password="123", name="Karl", surname="König", phonenumber="123456")
    user2 = User(e_mail="hey@ho.com", password="passwort", name="Bob", surname="Fischer", phonenumber="654321")
    user3 = User(e_mail="Mail@mail.com", password="456", name="Tim", surname="Meier", phonenumber="21")
    user4 = User(e_mail="a@a.a", password=" ", name="Wilhelm", surname="Schmidt", phonenumber="09123 12345-67")
    user4.is_admin = True
    user5 = User(e_mail="Testo@web.de", password="456", name="testo", surname="Testington", phonenumber="621")
    user5.is_admin = True
    user6 = User(e_mail="Jack@web.de", password="1234", name="Jack", surname="von Teststadt", phonenumber="+49045 1123")
    user7 = User(e_mail="mymail@gmail.com", password="abc", name="Billy", surname="Bob", phonenumber="651")
    users = (
        user1,
        user2,
        user3,
        user4,
        user5,
        user6,
        user7)

    for user in users:
        user.location = random.choice(locations)


    producer1 = Producer("ABB")
    producer2 = Producer("iEi")
    producer3 = Producer("Moxa")
    producer4 = Producer("Wago")
    producer5 = Producer("Phoenix Contact")
    producer6 = Producer("Padcon")
    producer7 = Producer("VIA Embedded")
    producer8 = Producer("Jetway")
    producer9 = Producer("Hirschmann")
    producers = (
        producer1,
        producer2,
        producer3,
        producer4,
        producer5,
        producer6,
        producer7,
        producer8,
        producer9)

    article1 = Article("CP-E 24/20.0")
    article2 = Article("EtherDevice Switch 316")
    article3 = Article("ioLogik E1241")
    article4 = Article("Managed Switch 852-104")
    article5 = Article("MINI-PS-100-240AC/5DC/3")
    article6 = Article("UIBX-250-BW")
    article7 = Article("PID Killer")
    article8 = Article("IPC AMOS-3005-1Q12A2")
    article9 = Article("IPC JBC323U591-3160-B")
    article10 = Article("IPC HM-1000")
    article11 = Article("MSwitch JRL116M-2F-M")
    article12 = Article("Switch SPIDER 8TX")
    article13 = Article("Switch SPIDER 5TX")
    article1.producer = producer1
    article2.producer = producer3
    article3.producer = producer3
    article4.producer = producer4
    article5.producer = producer5
    article6.producer = producer2
    article7.producer = producer6
    article8.producer = producer7
    article9.producer = producer8
    article10.producer = producer8
    article11.producer = producer8
    article12.producer = producer9
    article13.producer = producer9
    articles = (
        article1, 
        article2, 
        article3, 
        article4, 
        article5,
        article6,
        article7,
        article8, 
        article9, 
        article10, 
        article11, 
        article12,
        article13)

    devices = [Device(str(i)) for i in range(200)]
    resps = [Responsibility() for device in devices]
    for device, resp in zip(devices, resps):
        device.article = random.choice(articles)
        resp.user = random.choice(users)
        resp.location = random.choice(locations)
        resp.device = device
        
    Session = orm.sessionmaker(bind=engine)
    session = Session()

    session.add_all(locations)
    session.add_all(users)
    session.add_all(producers)
    session.add_all(articles)
    session.add_all(devices)
    session.add_all(resps)

    print("-"*30)
    print(f"{article1.producer.name} produces the following articles")
    for art in producer1.articles:
        print(f"{' '*5}{art.name}")
        print(f"{' '*10}instances of these articles are:")
        for device in art.devices:
            print(f"{device.code:>20} stored at {device.responsibility.location.name:<20}")
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
            print(f"{str(resp.user):^30}|{resp.device.code:^8}|{resp.location.name:^15}|{resp.device.article.name:^30}")

    for device in devices:
        print(f"id={device.uid} name={device.article.name}")

    session.commit()
    session.close()
