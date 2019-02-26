"""main module that ties everything together"""

import logging
import sys
import ctypes                                                               # --
from threading import Lock, Thread
from time import sleep

from PyQt5.QtWidgets import QApplication

from barcodereader import LazyVideoStream, VideoStream
from classes import VideoStreamUISync
from logger import logger
import ui
from utils import absolute_path

appid = u'Padcon.TUInventory.DesktopApp.1_0_0'                              # probably WONT WORK on Linux
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)        # --

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