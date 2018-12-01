import os
import sys
import pathlib
import styling

from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen
from PyQt5.QtCore import Qt

import classes
import slots

CSession = classes.setup_context_session(classes.engine)

def absolute_path(relative_path):
    path = pathlib.Path(os.path.dirname(__file__))
    return path / relative_path


class MainDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        path = absolute_path("main_horizontal.ui")
        super().__init__(parent)
        self.ui = uic.loadUi(path, self)
        self.logged_in_user = None
        self.set_tree()

        self.ui.b_user_login.clicked.connect(self.b_user_login_click)
        self.ui.b_user_logout.clicked.connect(self.b_user_logout_click)
        self.ui.b_home_1.clicked.connect(self.b_home_1_click)

        # tabs_click
        self.ui.b_tab_1.clicked.connect(self.b_tab_1_click)
        self.ui.b_tab_2.clicked.connect(self.b_tab_2_click)
        self.ui.b_tab_3.clicked.connect(self.b_tab_3_click)
        self.ui.b_tab_4.clicked.connect(self.b_tab_4_click)
        self.ui.b_tab_5.clicked.connect(self.b_tab_5_click)
        self.ui.b_tui_bottom.clicked.connect(self.b_tui_bottom_click)

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

        palette6 = self.line_6.palette()                    # line_bottom / blue
        role6 = self.line_6.backgroundRole()
        palette6.setColor(role6, QColor('blue'))
        self.ui.line_6.setPalette(palette6)
        self.ui.line_6.setAutoFillBackground(True)

        #palette7 = self.line_7.palette()                   # line_top / blue
        #role7 = self.line_7.backgroundRole()
        #palette7.setColor(role7, QColor('blue'))
        #self.ui.line_7.setPalette(palette7)
        #self.ui.line_7.setAutoFillBackground(True)

        palette8 = self.b_tui_bottom.palette()              # button_bottom / blue
        role8 = self.b_tui_bottom.backgroundRole()
        palette8.setColor(role8, QColor('blue'))
        self.ui.b_tui_bottom.setPalette(palette8)
        self.ui.b_tui_bottom.setAutoFillBackground(True)

        #palette9 = self.b_home_1.palette()                 # ist noch hässlich, muss überarbeitet werden
        #role9 = self.b_home_1.backgroundRole()
        #palette9.setColor(role9, QColor('blue'))
        #self.ui.b_home_1.setPalette(palette9)
        #self.ui.b_home_1.setAutoFillBackground(True)
        #self.b_home_1.setStyleSheet("color: white")
    #/#


    #*# show tabs
        self.ui.stackedWidget.setCurrentIndex(0)
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

    def b_tui_bottom_click(self):                       # home
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.line_1.show()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.hide()
        self.ui.line_5.hide()

    def b_tab_1_click(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.line_1.show()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.hide()
        self.ui.line_5.hide()

    def b_tab_2_click(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.line_1.hide()
        self.ui.line_2.show()
        self.ui.line_3.hide()
        self.ui.line_4.hide()
        self.ui.line_5.hide()

    def b_tab_3_click(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.line_1.hide()
        self.ui.line_2.hide()
        self.ui.line_3.show()
        self.ui.line_4.hide()
        self.ui.line_5.hide()

    def b_tab_4_click(self):
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.line_1.hide()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.show()
        self.ui.line_5.hide()

    def b_tab_5_click(self):
        self.ui.stackedWidget.setCurrentIndex(4)
        self.ui.line_1.hide()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.hide()
        self.ui.line_5.show()
    #/#    

    def set_tree(self): # toDo make tree scrollable if it gets too big
        with CSession() as session:
            responsibilities = session.query(classes.Responsibility).all()
            for resp in responsibilities:
                location = QtWidgets.QTreeWidgetItem([str(resp.location.name)])
                user = QtWidgets.QTreeWidgetItem([str(resp.user)]) # toDo: Set color if user is the currently logged in one and add this to update_user_dependant
                device = QtWidgets.QTreeWidgetItem([str(resp.device)])
                locations = [self.treeWidget.topLevelItem(i) for i in range(self.treeWidget.topLevelItemCount())] # has to be list-comprehension because used multiple times -> docu
                tree_text = (item.text(0) for item in locations) # can be generator expression because single-use -> docu
                if str(resp.location.name) not in tree_text: # if there's a device with the name of a location already displayed there's an issue
                    location.addChild(user)
                    user.addChild(device)
                    self.treeWidget.addTopLevelItem(location)
                else:
                    for location in locations:
                        if location.text(0) == str(resp.location):
                            users = [location.child(i) for i in range(location.childCount())]
                            if str(resp.user) not in (user.text(0) for user in users):
                                location.addChild(user)
                                user.addChild(device)
                            else:
                                for user in users:
                                    devices = (user.child(i) for i in range(location.childCount()))
                                    if str(resp.device) not in devices:
                                        user.addChild(device)

    def b_user_login_click(self):
        LoginDialog(self).exec() # show dialog_login as modal dialog => blocks controll of main
        self.update_user_dependant()
        print(self.logged_in_user)

    def b_user_logout_click(self):
        self.logged_in_user = None # may want slots.logout if that does something eventually
        self.update_user_dependant()

    def update_user_dependant(self):
        if self.logged_in_user:
            self.ui.log_in_out.setCurrentIndex(0)
            self.label.setText(str(self.logged_in_user).title())
        else:
            self.ui.log_in_out.setCurrentIndex(1)
            self.label.setText("")

class LoginDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None):
        path = absolute_path("login.ui")
        super().__init__(parent)
        self.parent = parent
        self.ui = uic.loadUi(path, self)
        self.b_login.clicked.connect(self.b_login_click)

    def b_login_click(self):
        username = self.t_username.text()
        password = self.t_password.text()
        self.parent.logged_in_user = slots.login(username, password)
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog_main = MainDialog()
    dialog_login = LoginDialog()
    dialog_main.show() # show dialog_main as modeless dialog => return control back immediately
    
    sys.exit(app.exec_())