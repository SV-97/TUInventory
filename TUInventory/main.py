"""main module that ties everything together"""
__version__ = "0.1.0"

import logging
import pathlib
import sys
from threading import Event, Thread
from time import sleep

from PyQt5.QtWidgets import QApplication

from barcodereader import LazyVideoStream, VideoStream
from classes import VideoStreamUISync, Timeout
from config import config
import keys
from logger import logger
import ui
from utils import absolute_path

if "win32" in sys.platform:
    import ctypes
    try:
        app_id = f"Padcon.TUInventory.DesktopApp.{__version__}"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except AttributeError as e:
        logger.debug(str(e))


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

def main():
    public_key_path = keys.PUBLIC_KEY_PATH
    if not public_key_path.exists():
        private_key_path = pathlib.Path("priv.key")
        keys.generate_key(public_key_path, private_key_path)
    app = QApplication(sys.argv)
    dialog_main = ui.MainDialog()
    dialog_main.showMaximized()
    
    try:
        videostream = LazyVideoStream()
        videostream.mirror = config["mirror"]
        videostream.start()
        logger.info(f"Camera {videostream.camera_id} succesfully opened")
        video_ui_sync_1 = VideoStreamUISync(
            dialog_main.ui.videoFeed, videostream, 
            dialog_main.code_recognized, "frames")
        video_ui_sync_2 = VideoStreamUISync(
            dialog_main.ui.videoFeed, videostream, 
            dialog_main.code_recognized, "codes")
        video_ui_sync_1.start()
        video_ui_sync_2.start()
        logger.info("Connected Camera to UI")
    except IOError as e:
        logger.error(str(e))

    
    settings_manager = SettingsManger(video_ui_sync_1, video_ui_sync_1, videostream)
    settings_manager.start()
    def setter(e):
        while True:
            sleep(20)
            e.set()

    signaller = Thread(target=setter, args=(settings_manager.event,))
    signaller.start()
    return app.exec_()


if __name__ == "__main__":
    # Profiling via terminal
    # import cProfile
    # cProfile.run("main()", sort="time")
    
    main()