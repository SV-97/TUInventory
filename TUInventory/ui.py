"""PyQt5 UI classes and linking to slots"""

import os
import pathlib
import re
import sys

from PyQt5 import uic, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QFileDialog, QPushButton, QStyle

import classes
from logger import logger
import slots
from utils import absolute_path, parallel_print, validate_filename, normalize_filename
from qr_generator import generate_qr

CSession = classes.setup_context_session(classes.engine)


class MainDialog(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        path = absolute_path("mainScaling.ui")
        super().__init__(parent)
        self.ui = uic.loadUi(path, self)
        self.logged_in_user = None
        self.savepath = None
        self.set_tree()
        self.set_combobox_location_u()
        self.set_combobox_location_d()
        self.set_combobox_producer_a()
        self.set_combobox_producer_d()
        self.set_combobox_article_d()
        self.set_combobox_user_d()
        self.setMouseTracking(True)


        icon = QtGui.QIcon()
        icon.addFile('pictures/256x256.png', QtCore.QSize(256,256))
        self.setWindowIcon(icon)


        self.ui.b_user_login.clicked.connect(self.b_user_login_click)
        self.ui.b_user_logout.clicked.connect(self.b_user_logout_click)
        self.ui.b_home_1.clicked.connect(self.b_home_1_click)
        self.ui.b_user_change.clicked.connect(self.b_user_change_click)
        self.ui.b_save_device.clicked.connect(self.b_save_device_click)
        self.ui.b_create_device.clicked.connect(self.b_create_device_click)
        self.ui.b_create_article.clicked.connect(self.b_create_article_click)
        self.ui.b_create_producer.clicked.connect(self.b_create_producer_click)
        self.ui.b_tab_1.clicked.connect(self.b_tab_1_click)
        self.ui.b_tab_2.clicked.connect(self.b_tab_2_click)
        self.ui.b_tab_3.clicked.connect(self.b_tab_3_click)
        self.ui.b_tab_4.clicked.connect(self.b_tab_4_click)
        self.ui.b_tab_5.clicked.connect(self.b_tab_5_click)

        self.ui.in_phone.textChanged.connect(self.set_phonenumber)

        self.ui.cb_producer_d.currentIndexChanged.connect(self.reload_combobox_article_d)


        self.setAutoFillBackground(True) # background / white
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

        palette1 = self.line_1.palette() # tab 1 / blue
        role1 = self.line_1.backgroundRole()
        palette1.setColor(role1, QColor('blue'))
        self.ui.line_1.setPalette(palette1)
        self.ui.line_1.setAutoFillBackground(True)

        palette2 = self.line_2.palette() # tab 2 / blue
        role2 = self.line_2.backgroundRole()
        palette2.setColor(role2, QColor('blue'))
        self.ui.line_2.setPalette(palette2)
        self.ui.line_2.setAutoFillBackground(True)

        palette3= self.line_3.palette() # tab 3 / blue
        role3 = self.line_3.backgroundRole()
        palette3.setColor(role3, QColor('blue'))
        self.ui.line_3.setPalette(palette3)
        self.ui.line_3.setAutoFillBackground(True)

        palette4 = self.line_4.palette() # tab 4 / blue
        role4 = self.line_4.backgroundRole()
        palette4.setColor(role4, QColor('blue'))
        self.ui.line_4.setPalette(palette4)
        self.ui.line_4.setAutoFillBackground(True)

        palette5 = self.line_5.palette() # tab 5 / blue
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
        self.update_user_dependant()

    def b_home_1_click(self): # home
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

    def set_tree(self):
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

    def set_combobox_location_u(self): # ComboBox for user creation
        self.cb_location_u.clear()
        with CSession() as session:
            locations = session.query(classes.Location).all()
            for location in locations:
                self.cb_location_u.addItem(location.name)
    
    def set_combobox_location_d(self): # ComboBox for device creation
        self.cb_location_d.clear()
        with CSession() as session:
            locations = session.query(classes.Location).all()
            for location in locations:
                self.cb_location_d.addItem(location.name)

    def set_combobox_producer_a(self):
        self.cb_producer_a.clear()
        with CSession() as session:
            producers = session.query(classes.Producer).all()
            for producer in producers:
                self.cb_producer_a.addItem(producer.name)
            
    def set_combobox_producer_d(self):
        self.cb_producer_d.clear()
        self.cb_producer_d.addItem("")
        with CSession() as session:
            producers = session.query(classes.Producer).all()
            for producer in producers:
                self.cb_producer_d.addItem(producer.name)

    def set_combobox_article_d(self):
        self.cb_article_d.clear()
        with CSession() as session:
            articles = session.query(classes.Article).all()
            for article in articles:
                self.cb_article_d.addItem(article.name)

    def reload_combobox_article_d(self):
        self.cb_article_d.clear()
        with CSession() as session:
            articles = session.query(classes.Article).all()
            producers = session.query(classes.Producer).all()
            producerX = str(self.cb_producer_d.currentText()) # todo: rework names
            if producerX:
                for producer in producers:
                    if producer.name == producerX:
                        self.producerXY = producer.uid
                        print (self.producerXY)
                for article in articles:
                    if article.producer_uid == self.producerXY:
                        self.cb_article_d.addItem(article.name)
            else:
                for article in articles:    
                    self.cb_article_d.addItem(article.name)

    def set_combobox_user_d(self):
        self.cb_user_d.clear()
        self.cb_user_d.addItem("")
        with CSession() as session:
            users = session.query(classes.User).all()
            for user in users:
                self.cb_user_d.addItem(f"{user.uid} {str(user)}")

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
        LoginDialog(self).exec()
        self.update_user_dependant()
        if self.logged_in_user:
            logger.info(f"Logged in as {self.logged_in_user}")
            self.timeout = classes.Timeout(60*15, lambda signal: signal.emit(True), self.ui.b_user_logout.clicked)
            self.timeout.start()

            # todo: these belong in update_user_dependant
            self.in_name.setText(self.logged_in_user.name) # fill textEdits for UserChange
            self.in_surname.setText(self.logged_in_user.surname)
            self.in_email.setText(self.logged_in_user.e_mail)
            #self.in_phone.setText(str(self.logged_in_user.phonenumber))

    def b_user_logout_click(self, timed_out=False):
        if timed_out:
            self.timed_out()
        self.logged_in_user = None # may want to use slots.logout if that does something eventually
        self.update_user_dependant()
        self.timeout.function = None
        del self.timeout
        self.in_name.setText("")
        self.in_surname.setText("")
        self.in_email.setText("")
        self.in_phone.setText("")

    def timed_out(self):
        logger.info(f"User {self.logged_in_user.uid} logged out due to inactivity")

        self.statusBar().setStyleSheet("color: #ff0000")   
        self.statusBar().showMessage("Sie wurden wegen Inaktivität automatisch ausgeloggt!", 5000)
        self.in_name.setText("")
        self.in_surname.setText("")
        self.in_email.setText("")
        self.in_phone.setText("")

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
                self.checkBox.setVisible(True)
            else:
                self.checkBox.setVisible(False)
        else:
            self.ui.log_in_out.setCurrentIndex(0)
            self.label.setText("")
            self.checkBox.setVisible(False)

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
        if "" in (box.text() for box in [self.in_name, self.in_surname, self.in_email, self.in_phone, self.in_password1, self.in_password2]):
            self.not_all_fields_filled_notice()
            return

        if self.checkBox.isChecked():
            user = slots.create_admin()
        else:
            user = slots.create_user()

        with CSession() as session:
            session.add(user)
            user.location = ... # queried location
            
        self.statusBar().setStyleSheet("color: green")   
        self.statusBar().showMessage("Benutzer {user} wurde erfolgreich angelegt.", 5000)

    def update_user(self):
        #toDo make User updateable
        pass

    def reset_password(self):
        """Set new password and salt for user, push it to db and show it in UI"""
        with CSession() as session:    
            # check if admin is logged in(though this dialog shouldn't show if no admin is logged in)
            # query user from db via name
            if self.logged_in_user.is_admin:
                user = session.query(classes.User).filter(classes.User.name)
            user = None
            new_password = slots.reset_password(user)
        # display password

    def b_save_device_click(self):
        qr_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if qr_path:
            self.t_path_device.setText(qr_path)

    def b_create_device_click(self): # todo: handle if logged in user is no admin and can't create devices for others
        article = self.cb_article_d.currentText()
        location = self.cb_location_d.currentText()
        user = self.cb_user_d.currentText()
        path = self.t_path_device.text()
        locals_ = {key: value for (key, value) in locals().items() if key != "self"}
        if "" in locals_.values():
            self.not_all_fields_filled_notice()
            return

        path = pathlib.Path(path)
        user_uid = int(user.split(" ")[0])
        with CSession() as session:
            article = session.query(classes.Article).filter_by(name=article).first()
            user = session.query(classes.User).filter_by(uid=user_uid).first()
            location = session.query(classes.Location).filter_by(name=location).first()
            device = classes.Device()
            session.add(device)
            device.article = article
            resp = classes.Responsibility(device, user, location)
            session.add(resp)
        path = pathlib.Path(self.t_path_device.text())
        if not re.match(r".*\.(svg)|(png)", str(path)):
            path = path / f"{device.uid}_{device.article.name}.svg"
            normalize_filename(str(path))
            
        validate_filename(path)
        generate_qr()

    def b_create_article_click(self):
        name = self.t_name_a.text()
        producer_name = self.cb_producer_a.currentText()
        locals_ = {key: value for (key, value) in locals().items() if key != "self"}
        if "" in locals_.values():
            self.not_all_fields_filled_notice()
            return
        with CSession() as session:
            producer = session.query(classes.Producer)\
                .filter_by(name=producer_name).first()
        try:
            slots.create_article(name=name, producer=producer)
        except classes.IntegrityError as e:
            logger.info(str(e))
            self.statusBar().setStyleSheet("color: red")
            self.statusBar().showMessage(f'Artikel mit Namen "{name}" existiert bereits.', 5000)
        else:
            self.statusBar().setStyleSheet("color: green")
            self.statusBar().showMessage(f'Artikel "{name}" wurde angelegt.', 5000)
        self.t_name_a.setText("")
        self.set_combobox_article_d()

    def b_create_producer_click(self):
        name = self.t_name_p.text()
        try:
            slots.create_producer(name=name)
        except classes.IntegrityError as e:
            logger.info(str(e))
            self.statusBar().setStyleSheet("color: red")
            self.statusBar().showMessage(f'Produzent mit Namen "{name}" existiert bereits.', 5000)
        else:
            self.statusBar().setStyleSheet("color: green")
            self.statusBar().showMessage(f'Produzent "{name}" wurde angelegt.', 5000)
        self.t_name_p.setText("")
        self.set_combobox_producer_d()
        self.set_combobox_producer_a()

    def not_all_fields_filled_notice(self):
        """Show message that user hasn't filled all necessary fields
        This could also be reworked to use signals and slots
        """
        self.statusBar().setStyleSheet("color: #ff0000")
        self.statusBar().showMessage("Bitte füllen Sie alle Felder aus", 5000)


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
    filepath = ""
    def __init__(self, parent=None):
        path = absolute_path("save.ui")
        super().__init__(parent)
        self.parent = parent
        self.ui = uic.loadUi(path, self)
        self.b_file_ok.clicked.connect(self.b_file_ok_click)
        self.b_close.clicked.connect(self.b_close_click)
        self.b_browse.clicked.connect(self.b_browse_click)
        self.t_path.setText(self.filepath)
    
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