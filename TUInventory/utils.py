import pathlib
import os
from queue import Queue
from threading import Thread

def absolute_path(relative_path):
    path = pathlib.Path(os.path.dirname(__file__))
    return path / relative_path

class _ParallelPrint(Thread):
    print_ = Queue()

    def __init__(self):
        super().__init__()
        self.daemon = True

    @classmethod
    def run(this):
        while True:
            val = this.print_.get()
            print(val)
            this.print_.task_done()


_ParallelPrint = _ParallelPrint()
_ParallelPrint.start()
parallel_print = _ParallelPrint.print_.put