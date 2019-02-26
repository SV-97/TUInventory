"""PyQt5 UI classes and linking to slots"""

import os, sys 

from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog

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
        self.savepath = None
        self.set_tree()
        self.set_combobox()
        
        self.setMouseTracking(True)

        self.ui.b_user_login.clicked.connect(self.b_user_login_click)
        self.ui.b_user_logout.clicked.connect(self.b_user_logout_click)
        self.ui.b_home_1.clicked.connect(self.b_home_1_click)
        self.ui.b_user_change.clicked.connect(self.b_user_change_click)
        self.ui.b_savepath.clicked.connect(self.b_savepath_click)
        self.ui.in_phone.textChanged.connect(self.set_phonenumber)

        # tabs_click
        self.ui.b_tab_1.clicked.connect(self.b_tab_1_click)
        self.ui.b_tab_2.clicked.connect(self.b_tab_2_click)
        self.ui.b_tab_3.clicked.connect(self.b_tab_3_click)
        self.ui.b_tab_4.clicked.connect(self.b_tab_4_click)
        self.ui.b_tab_5.clicked.connect(self.b_tab_5_click)

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

    def set_tree(self): # toDo make tree scrollable if it gets too big
        with CSession() as session:
            responsibilities = session.query(classes.Responsibility).all()
            for resp in responsibilities:
                location = QtWidgets.QTreeWidgetItem([str(resp.location.name)])
                user = QtWidgets.QTreeWidgetItem([str(resp.user)]) # toDo: Set color if user is the currently logged in one and add this to update_user_dependant
                device = QtWidgets.QTreeWidgetItem([str(resp.device)])
                locations = [self.treeWidget.topLevelItem(i) for i in range(self.treeWidget.topLevelItemCount())] # has to be list-comprehension because used multiple times -> docu
                tree_text = (item.text(0) for item in locations) # can be generator expression because single-use -> docu
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

    def set_combobox(self):
        with CSession() as session:
            locations = session.query(classes.Location).all()
            for location in locations:
                self.cb_location.addItem(location.name)

    def set_phonenumber(self, str_):
        try:
            if not str_:
                raise classes.PhoneNumber.NoNumberFoundWarning
            text = str(classes.PhoneNumber(str_))
        except classes.PhoneNumber.NoNumberFoundWarning:
            text = "Es konnte keine Nummer erkannt werden. Empfohlene Syntax ist: Vorwahl Benutzernummer-Durchwahl"    
        self.out_phone.setText(text)

    def b_user_login_click(self):
        LoginDialog(self).exec() # show dialog_login as modal dialog => blocks controll of main
        self.update_user_dependant()
        if self.logged_in_user:
            logger.info(f"Logged in as {self.logged_in_user}")
            self.timeout = classes.Timeout(5, lambda signal: signal.emit(True), (self.ui.b_user_logout.clicked,))
            self.timeout.start()

            #self.in_name.setText(self.logged_in_user.name)              # fill textEdits for UserChange
            #self.in_surname.setText(self.logged_in_user.surname)
            #self.in_email.setText(self.logged_in_user.email)
            #self.in_phone.setText(self.logged_in_user.phone)


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
            self.ui.log_in_out.setCurrentIndex(0)
            self.label.setText(str(self.logged_in_user).title()) 

            self.statusBar().setStyleSheet("color: #008080")
            self.statusBar().showMessage(f"Sie sind jetzt als {self.logged_in_user} angemeldet.", 1500)

            if self.logged_in_user.is_admin:
                self.checkBox.visible = True
            else:
                self.checkBox.visible = False 
        else:
            self.ui.log_in_out.setCurrentIndex(1)
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

    def b_savepath_click(self):
        SaveDialog(self).exec()
        if self.savepath:
            print(self.savepath)


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


class SaveDialog(QtWidgets.QDialog):        #Dialog to get select a filepath
         
    def __init__(self, parent=None):
        path = absolute_path("save.ui")
        super().__init__(parent)
        self.parent = parent
        self.ui = uic.loadUi(path, self)
        self.b_file_ok.clicked.connect(self.b_file_ok_click)
        self.b_close.clicked.connect(self.b_close_click)
        self.b_browse.clicked.connect(self.b_browse_click)
        self.filepath = None
    
    def b_browse_click(self):
        self.filename = "filename.svg"
        #self.filepath = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', "~/Desktop") #could be used to select a file
        self.filepath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory") + "/" + self.filename
        self.t_path.setText(self.filepath)

    def b_file_ok_click(self):
        self.parent.savepath = self.t_path.text()
        self.close()

    def b_close_click(self):
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog_main = MainDialog()
    dialog_login = LoginDialog()
    dialog_save = SaveDialog()

    dialog_main.show() # show dialog_main as modeless dialog => return control back immediately

    sys.exit(app.exec_())