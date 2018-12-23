"""logging interface for consistent formatting"""

import logging

from utils import absolute_path

handler = logging.FileHandler(filename=absolute_path("protocol.log"))
formatter = logging.Formatter(
    fmt='{asctime} [{levelname:8}] from {module:>15}.{funcName:12} "{message}"', 
    style="{", 
    datefmt="%Y-%m-%dT%H:%m:%S")

handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

del handler
del formatter