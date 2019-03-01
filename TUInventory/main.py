"""main module that ties everything together"""
__version__ = "0.1.0"

import logging
import sys
from threading import Lock, Thread
from time import sleep

from PyQt5.QtWidgets import QApplication

from barcodereader import LazyVideoStream, VideoStream
from classes import VideoStreamUISync
from logger import logger
import ui
from utils import absolute_path

if "win32" in sys.platform:
    import ctypes
    try:
        app_id = f"Padcon.TUInventory.DesktopApp.{__version__}"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass

def main():
    app = QApplication(sys.argv)
    dialog_main = ui.MainDialog()
    dialog_main.showMaximized()
    
    try:
        videostream = LazyVideoStream()
        videostream.start()
        logger.info(f"Camera {videostream.camera_id} succesfully opened")
        video_ui_sync = VideoStreamUISync(dialog_main.ui.videoFeed, videostream)
        video_ui_sync.start()
        logger.info("Connected Camera to UI")
    except IOError as e:
        logger.error(str(e))

    return app.exec_()


if __name__ == "__main__":
    # Profiling via terminal
    import cProfile
    cProfile.run("main()", sort="time")
    
    #sys.exit(main())