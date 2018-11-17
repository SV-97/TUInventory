import os
import sys
import pathlib
import sqlite3

from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen
from PyQt5.QtCore import Qt

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

        # tabs_click
        self.ui.b_tab_1.clicked.connect(self.b_tab_1_click)
        self.ui.b_tab_2.clicked.connect(self.b_tab_2_click)
        self.ui.b_tab_3.clicked.connect(self.b_tab_3_click)
        self.ui.b_tab_4.clicked.connect(self.b_tab_4_click)
        self.ui.b_tab_5.clicked.connect(self.b_tab_5_click)

    #*# set Colors
        self.setAutoFillBackground(True)                    # background / white
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

        palette1 = self.line_1.palette()                    # tab 1 / blue
        role1 = self.line_1.backgroundRole()
        palette1.setColor(role1, QColor('blue'))
        self.ui.line_1.setPalette(palette1)
        self.ui.line_1.setAutoFillBackground(True)

        palette2 = self.line_2.palette()                    # tab 2 / blue
        role2 = self.line_2.backgroundRole()
        palette2.setColor(role2, QColor('blue'))
        self.ui.line_2.setPalette(palette2)
        self.ui.line_2.setAutoFillBackground(True)

        palette3= self.line_3.palette()                     # tab 3 / blue
        role3 = self.line_3.backgroundRole()
        palette3.setColor(role3, QColor('blue'))
        self.ui.line_3.setPalette(palette3)
        self.ui.line_3.setAutoFillBackground(True)

        palette4 = self.line_4.palette()                    # tab 4 / blue
        role4 = self.line_4.backgroundRole()
        palette4.setColor(role4, QColor('blue'))
        self.ui.line_4.setPalette(palette4)
        self.ui.line_4.setAutoFillBackground(True)

        palette5 = self.line_5.palette()                    # tab 5 / blue
        role5 = self.line_5.backgroundRole()
        palette5.setColor(role5, QColor('blue'))
        self.ui.line_5.setPalette(palette5)
        self.ui.line_5.setAutoFillBackground(True)
    #/#

    #*# show tabs
        self.ui.line_1.show()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.hide()
        self.ui.line_5.hide()

    def b_home_1_click(self):                       # home
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.line_1.show()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.hide()
        self.ui.line_5.hide()

    def b_tab_1_click(self):                        # tab 1
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.line_1.show()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.hide()
        self.ui.line_5.hide()

    def b_tab_2_click(self):                        # tab 2
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.line_1.hide()
        self.ui.line_2.show()
        self.ui.line_3.hide()
        self.ui.line_4.hide()
        self.ui.line_5.hide()

    def b_tab_3_click(self):                        # tab 3
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.line_1.hide()
        self.ui.line_2.hide()
        self.ui.line_3.show()
        self.ui.line_4.hide()
        self.ui.line_5.hide()

    def b_tab_4_click(self):                        # tab 4
        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.line_1.hide()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.show()
        self.ui.line_5.hide()

    def b_tab_5_click(self):                        # tab 5
        # self.ui.stackedWidget.setCurrentIndex(4)
        self.ui.line_1.hide()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.hide()
        self.ui.line_5.show()
    #/#    
    
    
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