import os
import sys
import pathlib
import sqlite3

from PyQt5 import QtWidgets, uic

import adapters
from classes import User

connection_users = sqlite3.connect("tuinventory.db")

def absolute_path(relative_path):
    path = pathlib.Path(os.path.dirname(__file__))
    return path / relative_path


class MainDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        path = absolute_path("main_horizontal.ui")
        super().__init__(parent)
        self.ui = uic.loadUi("main_horizontal.ui", self)
        self.ui.b_user_login.clicked.connect(self.b_user_login_click)
        self.ui.b_user_logout.clicked.connect(self.b_user_logout_click)
        self.ui.b_home_1.clicked.connect(self.b_home_1_click)

        self.ui.b_tab_1.clicked.connect(self.b_tab_1_click)
        self.ui.b_tab_2.clicked.connect(self.b_tab_2_click)
        self.ui.b_tab_3.clicked.connect(self.b_tab_3_click)
        self.ui.b_tab_4.clicked.connect(self.b_tab_4_click)

##
        self.ui.line_1.show()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.hide()

    def b_home_1_click(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.line_1.show()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.hide()

    def b_tab_1_click(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.line_1.show()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.hide()

    def b_tab_2_click(self):
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.line_1.hide()
        self.ui.line_2.show()
        self.ui.line_3.hide()
        self.ui.line_4.hide()

    def b_tab_3_click(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.line_1.hide()
        self.ui.line_2.hide()
        self.ui.line_3.show()
        self.ui.line_4.hide()

    def b_tab_4_click(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.line_1.hide()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.show()
##    
    
    
    def b_user_login_click(self):
        global dialog_login
        dialog_login.exec() # show dialog_login as modal dialog => blocks controll of main
        self.hide()
        self.ui.log_in_out.setCurrentIndex(0)

    def b_user_logout_click(self):
        self.ui.log_in_out.setCurrentIndex(1)


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        path = absolute_path("login.ui")
        super().__init__(parent)
        self.ui = uic.loadUi(path, self)
        self.b_login.clicked.connect(self.b_login_click)
    def b_login_click(self):
        connection = connection_users
        username = self.t_username.text()
        password = self.t_password.text()
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT user FROM users WHERE username=?", username)
            user = cursor.fetchall()
        if user:
            pass # proceed with log in/check password, close dialog
        else:
            pass # show error message


app = QtWidgets.QApplication(sys.argv)
dialog_main = MainDialog()
dialog_login = LoginDialog()
dialog_main.show() # show dialog_main as modeless dialog => return control back immediately

sys.exit(app.exec_())