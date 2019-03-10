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


def check_if_file_exists(path):
    """Check whether a file already exists, create directories in path that don't exist yet"""
    try:
        with open(path, "x"):
            pass
    except FileExistsError as e:
        return False
    except FileNotFoundError:
        path.parents[0].mkdir(parents=True)
        return True
    else:
        os.remove(path)
        return True


def normalize_filename(string):
    """Remove all non ASCII letters and digits from a string and 
    replace whitespaces with underscores keeping dots untouched"""
    string = umlaut_converter(string)
    segs = string.split(".")
    for i, seg in enumerate(segs):
        segs[i] = re.sub(r"[\s]", "_", segs[i])
        segs[i] = re.sub(r"[\W]", "", seg, flags=re.ASCII)
    return ".".join(segs)
    

def umlaut_converter(string):
    """Convert all umlauts to their e-equivalent"""
    return string.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")