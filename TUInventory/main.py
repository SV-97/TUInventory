from collections import Counter
import sys
from threading import Lock, Thread
from time import sleep

import cv2
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QImage, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt

from barcodereader import LazyVideoStream, VideoStream
from logger import logger
import ui

class VideoStreamToUISync(Thread):
    def __init__(self, canvas, videostream):
        """Class to tie a LazyVideoStream to some canvas in Qt
        Args:
            canvas: canvas has to be able to take pixmaps/implement setPixmap
            videostream: Instance of LazyVideoStream that supplies the frames
        """
        super().__init__()
        self.canvas = canvas
        self.videostream = videostream
        self.daemon = True
        self.barcodes = Counter()
        self.barcode_lock = Lock()

    @staticmethod
    def _matrice_to_QPixmap(frame):
        height, width, channel = frame.shape
        image = QImage(frame.data, width, height, 3 * width, QImage.Format_RGB888)
        return QPixmap(image)

    def get_most_common(self):
        with self.barcode_lock:
            return self.barcodes.most_common(1)[0]

    def run(self):
        while True:
            videostream.request_queue.put(True)
            frame, found_codes = videostream.frame_queue.get()
            pixmap = self._matrice_to_QPixmap(frame)
            self.canvas.setPixmap(pixmap)
            if found_codes:
                self.barcodes.update(found_codes)
            cv2.waitKey(1)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog_main = ui.MainDialog()
    dialog_login = ui.LoginDialog()

    videostream = LazyVideoStream()
    videostream.start()
    video_ui_sync = VideoStreamToUISync(dialog_main.ui.videoFeed, videostream)
    video_ui_sync.start()
    
    dialog_main.show() # show dialog_main as modeless dialog => return control back immediately
        
    """
    if counter:
        code = 
        if code[1] > 20:
            print(code[0])
            cv2.destroyWindow(window)
            sleep(5)
            return"""

    sys.exit(app.exec_())
