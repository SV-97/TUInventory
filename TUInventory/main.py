"""main module that ties everything together"""
__version__ = "0.3.0"

import logging
import pathlib
import sys
from time import sleep

from PyQt5.QtWidgets import QApplication

from barcodereader import LazyVideoStream, VideoStream
from classes import VideoStreamUISync, Timeout
from config import config, SettingsManger
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


class Dummy():
    pass


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
        videostream = Dummy()
        video_ui_sync_1 = Dummy()
        video_ui_sync_2 = Dummy()
    
    settings_manager = SettingsManger(video_ui_sync_1, video_ui_sync_2, videostream)
    settings_manager.start()
    dialog_main.settings_event = settings_manager.event
    return app.exec_()


if __name__ == "__main__":
    # Profiling via terminal
    # import cProfile
    # cProfile.run("main()", sort="time")
    
    main()