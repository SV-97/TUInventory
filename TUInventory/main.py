#import logging
import sys

import cv2
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen
from PyQt5.QtCore import Qt

from barcodereader import VideoStream
#import logger
import ui


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog_main = ui.MainDialog()
    dialog_login = ui.LoginDialog()

    videostream = VideoStream()
    videostream.start()
    
    dialog_main.show() # show dialog_main as modeless dialog => return control back immediately
    cv2.namedWindow("window")
    while True:
        cv2.imshow("window", videostream.frame)
        cv2.waitKey(1)
    """
    if counter:
        code = Counter(counter).most_common(1)[0]
        if code[1] > 20:
            print(code[0])
            cv2.destroyWindow(window)
            sleep(5)
            return"""

    sys.exit(app.exec_())
