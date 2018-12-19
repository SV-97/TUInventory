import pathlib
import os

def absolute_path(relative_path):
    path = pathlib.Path(os.path.dirname(__file__))
    return path / relative_path