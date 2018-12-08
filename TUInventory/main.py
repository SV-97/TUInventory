import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen
from PyQt5.QtCore import Qt

import ui
from barcodereader import VideoStream

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog_main = ui.MainDialog()
    dialog_login = ui.LoginDialog()

    videostream = VideoStream()
    # videostream.start()

    dialog_main.show() # show dialog_main as modeless dialog => return control back immediately

    """
    if counter:
        code = Counter(counter).most_common(1)[0]
        if code[1] > 20:
            print(code[0])
            cv2.destroyWindow(window)
            sleep(5)
            return"""

    sys.exit(app.exec_())
