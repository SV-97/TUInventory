import os
import sys
import pathlib

from PyQt5 import QtWidgets, uic

# 39.3 - S. 839

qt_creator_file = "login.ui"
path = pathlib.Path(os.path.dirname(__file__)) / qt_creator_file

class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = uic.loadUi(path, self)

app = QtWidgets.QApplication(sys.argv)
dialog_login = LoginDialog()
dialog_login.show()
sys.exit(app.exec_())