"""PyQt5 UI classes and linking to slots"""

import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen
from PyQt5.QtCore import Qt

import classes
from logger import logger
import slots
from utils import absolute_path, parallel_print

CSession = classes.setup_context_session(classes.engine)


class MainDialog(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        path = absolute_path("mainScaling.ui")
        super().__init__(parent)
        self.ui = uic.loadUi(path, self)
        self.logged_in_user = None
        self.set_tree()
        self.set_combobox()
        
        self.setMouseTracking(True)

        self.ui.b_user_login.clicked.connect(self.b_user_login_click)
        self.ui.b_user_logout.clicked.connect(self.b_user_logout_click)
        self.ui.b_home_1.clicked.connect(self.b_home_1_click)
        self.ui.b_user_change.clicked.connect(self.b_user_change_click)

        self.ui.in_phone.textChanged.connect(self.set_phonenumber)

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

        #palette7 = self.line_7.palette()                   # line_top / blue
        #role7 = self.line_7.backgroundRole()
        #palette7.setColor(role7, QColor('blue'))
        #self.ui.line_7.setPalette(palette7)
        #self.ui.line_7.setAutoFillBackground(True)
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
        self.treeWidget.clear()
        with CSession() as session:
            locations = session.query(classes.Location).all()
            locations.sort(key=lambda loc: loc.name)
            for location in locations:
                users = session.query(classes.User).join(classes.Responsibility).\
                    filter_by(location=location).all()
                users.sort(key=lambda user: str(user))
                if users:
                    location_item = QtWidgets.QTreeWidgetItem([str(location.name)])
                    self.treeWidget.addTopLevelItem(location_item)
                else:
                    continue
                for user in users:
                    devices = session.query(classes.Device).join(classes.Responsibility).\
                        filter_by(user=user, location=location).all()
                    user_item = QtWidgets.QTreeWidgetItem([str(user)])
                    devices.sort(key=lambda device: str(device))
                    location_item.addChild(user_item)
                    for device in devices:
                        device_item = QtWidgets.QTreeWidgetItem([str(device)])
                        user_item.addChild(device_item)

            """
            responsibilities = session.query(classes.Responsibility).all()
            responsibilities.sort(key=lambda resp: resp.device.uid)
            for resp in responsibilities:
                print()
                print(f"New Resp: {resp.location.uid}.{resp.user.uid}.{resp.device.uid} | {resp.user.name:^15} | {resp.location.name:^15}")
                location = QtWidgets.QTreeWidgetItem([str(resp.location.name)])
                user = QtWidgets.QTreeWidgetItem([str(resp.user)])
                device = QtWidgets.QTreeWidgetItem([str(resp.device)])
                locations = [self.treeWidget.topLevelItem(i) for i in range(self.treeWidget.topLevelItemCount())]
                tree_text = [item.text(0) for item in locations]
                if str(resp.location.name) not in tree_text:
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
                """

    def set_combobox(self):
        with CSession() as session:
            locations = session.query(classes.Location).all()
            for location in locations:
                self.cb_location.addItem(location.name)

    def set_phonenumber(self, str_):
        if str_:
            try:
                text = str(classes.PhoneNumber(str_))
            except classes.PhoneNumber.NoNumberFoundWarning:
                text = "Es konnte keine Nummer erkannt werden. Empfohlene Syntax ist: Vorwahl Benutzernummer-Durchwahl"    
        else:
            text = "Bitte geben Sie Ihre Telefonnummer ein."
        self.out_phone.setText(text)

    def b_user_login_click(self):
        LoginDialog(self).exec() # show dialog_login as modal dialog => blocks controll of main
        self.update_user_dependant()
        if self.logged_in_user:
            logger.info(f"Logged in as {self.logged_in_user}")
            self.timeout = classes.Timeout(5, lambda signal: signal.emit(True), self.ui.b_user_logout.clicked)
            self.timeout.start()

    def b_user_logout_click(self, timed_out=False):
        if timed_out:
            self.timed_out()
        self.logged_in_user = None # may want slots.logout if that does something eventually
        self.update_user_dependant()
        self.timeout.function = None
        del self.timeout

    def timed_out(self):
        logger.info(f"User {self.logged_in_user.uid} logged out due to inactivity")

        self.statusBar().setStyleSheet("color: #ff0000")   
        self.statusBar().showMessage("Sie wurden wegen Inaktivität automatisch ausgeloggt!", 2000)

        messagebox = QtWidgets.QMessageBox()
        messagebox.setIcon(QtWidgets.QMessageBox.Information)
        messagebox.setWindowTitle("Automatisch ausgeloggt")
        messagebox.setText("Sie wurden wegen Inaktivität automatisch ausgeloggt!")
        messagebox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        messagebox.exec_()

    def update_user_dependant(self):
        if self.logged_in_user:
            self.ui.log_in_out.setCurrentIndex(1)
            self.label.setText(str(self.logged_in_user)) 

            self.statusBar().setStyleSheet("color: #008080")
            self.statusBar().showMessage(f"Sie sind jetzt als {self.logged_in_user} angemeldet.", 1500)
            
            if self.logged_in_user.is_admin:
                self.checkBox.visible = True
            else:
                self.checkBox.visible = False 
        else:
            self.ui.log_in_out.setCurrentIndex(0)
            self.label.setText("")

    def mousePressEvent(self, QMouseEvent=None):
        print("Maus geklickt")
        self.mouseMoveEvent()
    
    def mouseMoveEvent(self, QMouseEvent=None):
        if QMouseEvent is not None:
            print("Maus bewegt")
        if hasattr(self, "timeout"):
            self.timeout.reset()

    def b_user_change_click(self): #toDo finish linked classes
        if self.logged_in_user:
            self.update_user()
        else:
            self.new_user()

    def new_user(self):
        if "" in (box.text() for box in [self.in_name, self.in_surname, self.in_email, self.in_phone]):
            self.statusBar().setStyleSheet("color: #ff0000")
            self.statusBar().showMessage("Bitte füllen Sie alle Felder aus", 5000)
            return
        
        args = [None for i in range(6)]
        user = slots.create_user(*args) # add textboxes once names are final and remove args
        if self.checkBox.isChecked():
            slots.create_admin(user)

        self.statusBar().setStyleSheet("color: green")   
        self.statusBar().showMessage("Benutzer {user} wurde erfolgreich angelegt.", 5000)

    #def update_user():
        #toDo make User updateable

    def reset_password(self):
        """Set new password and salt for user, push it to db and show it in UI"""
        with CSession() as session:    
            # check if admin is logged in(though this dialog shouldn't show if no admin is logged in)
            # query user from db via name
            user = None
            new_password = slots.reset_password(user)
        # display password

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