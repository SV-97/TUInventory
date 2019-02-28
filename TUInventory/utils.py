"""General utilities independet of the other modules"""

import pathlib
import os
from queue import Queue
import re
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
            raise ResourceWarning(f"{self.__class__.__name__} should only be instantiated once!")
        super().__init__(name=f"{self.__class__.__name__}Thread")
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


def validate_filename(path):
    """Validate if file already exists"""
    try:
        open(path, "x")
    except FileExistsError as e:
        return False
    else:
        os.remove(path)
        return True


def normalize_filename(string):
    """Remove all non ASCII letters and digits from a string and 
    replace whitespaces with underscores keeping dots untouched"""
    segs = string.split(".")
    for i, seg in enumerate(segs):
        segs[i] = re.sub(r"[\W][^\s]", "", seg, flags=re.ASCII)
        segs[i] = re.sub(r"[\s]", "_", segs[i])
    return ".".join(segs)
    

if __name__ == "__main__":
    assert normalize_filename("123abd.edg/(&(&(%§!14    g\n1gj2141.pdf") == "123abd.edg4___gj2141.pdf"

    assert validate_filename("abc") == True
    with open("abc", "w") as f:
        assert validate_filename("abc") == False
    os.remove("abc")