"""Wrapper around configparser API for dict-like access"""

import builtins
import configparser
import re
from threading import Event, Thread

from utils import absolute_path


class ConfigParserDict(configparser.ConfigParser):
    """Allow dict-like access to config items with main as standard-section"""
    def __init__(self, config_file=absolute_path("config.ini")):
        super().__init__()
        self.config_file = config_file

    @staticmethod
    def _key_conv(key):
        """Convert an index-key into section and key"""
        if type(key) == tuple:
            section, key = key
        else:
            section = "main"
        return section, key

    @staticmethod
    def _autotype(val):
        """Converts string of type f"{type(val)}{val}" to type(val)"""
        match = re.match(r"<class '(?P<type>.*)'> (?P<val>.*)", val)
        type_ = match.group("type")
        val = match.group("val")
        if type_ == bool and val=="False":
            return False
        return getattr(builtins, type_)(val)

    def __getitem__(self, key):
        section, key = self._key_conv(key)
        return self._autotype(self.get(section, key))

    def __setitem__(self, key, value):
        section, key = self._key_conv(key)
        value = f"{type(value)} {value}"
        try:
            self.set(section, key, value)
        except configparser.NoSectionError:
            self.add_section(section)
            self.set(section, key, value)

    def flush(self):
        with open(self.config_file, "w") as f:
            self.write(f)

    def read(self):
        return super().read(self.config_file)

config = ConfigParserDict()
if not config.config_file.exists():
    config["mirror"] = True
    config["qr_path"] = ""
    config["timeout"] = 15.0
    config.flush()
config.read()


class SettingsManger(Thread):
    def __init__(self, video_ui_sync_1, video_ui_sync_2, videostream):
        super().__init__(name=f"{self.__class__.__name__}Thread_{id(self)}")
        self.video_ui_sync_1 = video_ui_sync_1
        self.video_ui_sync_2 = video_ui_sync_2
        self.videostream = videostream
        self.event = Event()
        self.daemon = True

    def run(self):
        while True:
            self.event.wait()
            self.event.clear()
            config.read()
            self.videostream.mirror = config["mirror"]