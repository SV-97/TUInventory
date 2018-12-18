import logging

from ui import absolute_path

logging.basicConfig(
    filename=absolute_path("protocol.log"), 
    level=logging.INFO,
    style="{",
    format='{asctime} [{levelname:8}] from {module:>15}.{funcName:12} "{message}" ',
    datefmt="%Y-%m-%dT%H:%m:%S")

logging.error("testerror")