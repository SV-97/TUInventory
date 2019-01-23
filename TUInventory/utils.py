"""General utilities independet of the other modules"""

import pathlib
import os
from queue import Queue
from threading import Thread

def absolute_path(relative_path):
    """Convert a path relative to the sourcefile to an absolute one"""
    path = pathlib.Path(os.path.dirname(__file__))
    return path / relative_path

class _ParallelPrint(Thread):
    """Provides a threadsafe print, instantiation below"""
    print_ = Queue()
    _created = False
    def __init__(self):
        if self._created:
            raise ResourceWarning(f"{self.__class__} should only be instantiated once!")
        super().__init__()
        self.daemon = True
        self.__class__._created = True

    @classmethod
    def run(cls):
        while True:
            val = cls.print_.get()
            print(val)
            cls.print_.task_done()

    @classmethod
    def __call__(cls):
        raise ResourceWarning(f"{cls.__class__} should only be instantiated once!")


_ParallelPrint = _ParallelPrint()
_ParallelPrint.start()
parallel_print = _ParallelPrint.print_.put