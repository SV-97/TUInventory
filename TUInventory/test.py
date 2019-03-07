from collections import Counter
from queue import Queue
from threading import Thread
from time import sleep


class Singleton(type):
    """Prevent a class from being instantiated more than once"""
    counter = Counter()
    def __call__(self):
        cls = super().__call__()
        self.counter.update((cls.__class__,))
        if self.counter[cls.__class__] > 1:
            raise ResourceWarning(
                f"{cls.__class__.__name__} should only be instantiated once!")
        return cls


class _ParallelPrint(Thread, metaclass=Singleton):
    """Provides a threadsafe print, instantiation below"""
    print_ = Queue()
    def __init__(self):
        super().__init__(name=f"{self.__class__.__name__}Thread")
        self.daemon = True
        self.__class__._created = True

    @classmethod
    def run(cls):
        while True:
            val = cls.print_.get()
            print(val)
            cls.print_.task_done()


printer = _ParallelPrint()
printer.start()
print_ = printer.print_.put