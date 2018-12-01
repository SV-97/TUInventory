import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen
from PyQt5.QtCore import Qt

import ui

app = QtWidgets.QApplication(sys.argv)
dialog_main = ui.MainDialog()
dialog_login = ui.LoginDialog()
dialog_main.exec() # show dialog_main as modeless dialog => return control back immediately
sys.exit(app.exec_())
