"""PyQt5 UI classes and linking to slots"""

import os
import pathlib
import re
import sys

from PyQt5 import uic, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QPushButton, QStyle

import classes
from config import config
import keys
from logger import logger
import slots
import utils
from qr_generator import generate_qr

CSession = classes.setup_context_session(classes.engine)


class MainDialog(QtWidgets.QMainWindow):
    code_recognized = pyqtSignal(str)

    def __init__(self, parent=None):
        path = utils.absolute_path("mainScaling.ui")
        super().__init__(parent)
        self.ui = uic.loadUi(path, self)
        self.logged_in_user = None
        self.savepath = None
        self.set_tree()
        self.set_combobox_location_u()
        self.set_combobox_location_u_admin()
        self.set_combobox_location_d()
        self.set_combobox_producer_a()
        self.set_combobox_producer_d()
        self.set_combobox_device_user()
        self.set_combobox_device_location()
        self.set_combobox_article_d()
        self.set_combobox_user_d()
        self.set_combobox_user_admin()
        self.setMouseTracking(True)
        
        self.ui.rb_mirror_yes.setChecked(config["mirror"])
        self.ui.rb_mirror_no.setChecked(not config["mirror"])

        self.t_path_device.setText(config["qr_path"])
       
        icon = QtGui.QIcon()
        icon_path = utils.absolute_path("pictures/TUI_Logo.png")
        icon.addFile(f"{icon_path}", QtCore.QSize(256,256))
        self.setWindowIcon(icon)

        self.ui.b_user_login.clicked.connect(self.b_user_login_click)
        self.ui.b_create_new_qrcode.clicked.connect(self.b_create_new_qrcode_click)
        self.ui.b_user_logout.clicked.connect(self.b_user_logout_click)
        self.ui.b_home_1.clicked.connect(self.b_home_1_click)
        self.ui.b_user_change.clicked.connect(self.b_user_change_click)
        self.ui.b_user_change_admin.clicked.connect(self.b_user_change_admin_click)
        self.ui.b_user_reset_admin.clicked.connect(self.reset_password)
        self.ui.b_save_device.clicked.connect(self.b_save_device_click)
        self.ui.b_change_device.clicked.connect(self.b_change_device_click)
        self.ui.b_delete_device.clicked.connect(self.b_delete_device_click)
        self.ui.b_create_device.clicked.connect(self.b_create_device_click)
        self.ui.b_create_article.clicked.connect(self.b_create_article_click)
        self.ui.b_create_producer.clicked.connect(self.b_create_producer_click)
        self.ui.b_qr_path.clicked.connect(self.b_qr_path_click)
        self.ui.b_save_settings.clicked.connect(self.mirror_setting)
        self.ui.b_tab_1.clicked.connect(self.b_tab_1_click)
        self.ui.b_tab_2.clicked.connect(self.b_tab_2_click)
        self.ui.b_tab_3.clicked.connect(self.b_tab_3_click)
        self.ui.b_tab_4.clicked.connect(self.b_tab_4_click)
        self.ui.b_tab_5.clicked.connect(self.b_tab_5_click)
        self.ui.in_phone.textChanged.connect(self.set_phonenumber)
        self.ui.in_phone_admin.textChanged.connect(self.set_phonenumber)
        self.ui.cb_producer_d.currentIndexChanged.connect(self.reload_combobox_article_d)
        self.ui.cb_user_admin.currentIndexChanged.connect(self.reload_user_change)

        foldericon_path = utils.absolute_path("pictures/folder.png")
        self.ui.b_save_device.setIcon(QtGui.QIcon(f"{foldericon_path}"))
        self.ui.b_save_device.setIconSize(QtCore.QSize(20,20))
        self.ui.b_qr_path.setIcon(QtGui.QIcon(f"{foldericon_path}"))
        self.ui.b_qr_path.setIconSize(QtCore.QSize(20,20))

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

        palette7 = self.bottom_frame.palette() # bottomframe
        role7 = self.bottom_frame.backgroundRole()
        palette7.setColor(role7, QColor('blue'))
        self.ui.bottom_frame.setPalette(palette7)
        self.ui.bottom_frame.setAutoFillBackground(True)
        self.ui.bottom_frame.setStyleSheet("color: white")

        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.line_1.show()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.hide()
        self.ui.line_5.hide()
        self.update_user_dependant()
        self.code_recognized.connect(self.recognized_barcode)

        self.ui.t_setting_timeout.setText(str(config["timeout"]))
        self.ui.t_setting_qr_path.setText(config["qr_path"])


    def status_bar_text(self, text, time, color):
        self.ui.label_status.setStyleSheet(f"color: {color}")
        self.ui.label_status.setText(text)
        self.timeout = classes.Timeout(time, MainDialog.status_bar_clear, self)
        self.timeout.start()
    
    def status_bar_clear(self):
        self.ui.label_status.setStyleSheet("color: black")
        self.ui.label_status.setText("")

    def mirror_setting(self):
        """Save settings to config.ini"""
        if self.ui.rb_mirror_yes.isChecked():
            mirror = True
        else:
            mirror = False

        timeout = float(self.ui.t_setting_timeout.text())
        if timeout < 1.9:
            timeout = config["timeout"]
            self.status_bar_text("Bitte geben Sie einen Wert von mindestens zwei Minuten ein", 4, "red") 
            return
        
        qr_path = self.ui.t_setting_qr_path.text()

        settings = [mirror, timeout, qr_path]
        conf = [config["mirror"], config["timeout"], config["qr_path"]]

        if not all(True if x==y else False for (x,y) in zip(settings, conf)):           
            #check if changes are made
            config["mirror"] = mirror
            config["timeout"] = timeout
            config["qr_path"] = qr_path   
            config.flush()
            self.status_bar_text("Ihre Einstellungen wurden erfolgreich gespeichert", 3, "green") 
            self.settings_event.set()
        else:
            self.status_bar_text("Es wurden keine Änderungen vorgenommen", 3, "green")

    def b_qr_path_click(self):
        """Show selected path in textbox"""     
        qr_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Bitte wählen Sie ein Verzeichnis")
        if qr_path:
            self.t_setting_qr_path.setText(qr_path)
            config["qr_path"] = f"{qr_path}"

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
        self.ui.line_1.hide()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.show()
        self.ui.line_5.hide()
        self.ui.stackedWidget.setCurrentIndex(4)
        if self.logged_in_user:
            if self.logged_in_user.is_admin:
                self.ui.stackedWidget.setCurrentIndex(3)         

    def b_tab_5_click(self):
        self.ui.stackedWidget.setCurrentIndex(5)
        self.ui.line_1.hide()
        self.ui.line_2.hide()
        self.ui.line_3.hide()
        self.ui.line_4.hide()
        self.ui.line_5.show() 

    def set_tree(self):
        """Fill main screen treeWidget"""
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

    def set_combobox_location_u(self):
        """Fill Location ComboBox for User creation"""
        self.cb_location_u.clear()
        with CSession() as session:
            locations = session.query(classes.Location).all()
            locations.sort(key=lambda location: str(location))
            for location in locations:
                self.cb_location_u.addItem(location.name)

    def set_combobox_location_u_admin(self):
        """Fill Location ComboBox for User creation"""
        self.cb_location_u_admin.clear()
        with CSession() as session:
            locations = session.query(classes.Location).all()
            locations.sort(key=lambda location: str(location))
            for location in locations:
                self.cb_location_u_admin.addItem(location.name)
    
    def set_combobox_location_d(self):
        """Fill Location ComboBox for Device creation"""
        self.cb_location_d.clear()
        with CSession() as session:
            locations = session.query(classes.Location).all()
            locations.sort(key=lambda location: str(location))
            for location in locations:
                self.cb_location_d.addItem(location.name)

    def set_combobox_producer_a(self):
        """Fill Producer ComboBox for Article creation"""
        self.cb_producer_a.clear()
        with CSession() as session:
            producers = session.query(classes.Producer).all()
            producers.sort(key=lambda producer: str(producer.name))
            for producer in producers:
                self.cb_producer_a.addItem(producer.name)
            
    def set_combobox_producer_d(self):
        """Fill Producer ComboBox for Device creation"""
        self.cb_producer_d.clear()
        self.cb_producer_d.addItem("")
        with CSession() as session:
            producers = session.query(classes.Producer).all()
            producers.sort(key=lambda producer: str(producer.name))
            for producer in producers:
                self.cb_producer_d.addItem(producer.name)

    def set_combobox_article_d(self):
        """Fill Article ComboBox for Device creation"""
        self.cb_article_d.clear()
        with CSession() as session:
            articles = session.query(classes.Article).all()
            for article in articles:
                self.cb_article_d.addItem(article.name)

    def reload_combobox_article_d(self):
        """Change article depending on selected Producer"""
        self.cb_article_d.clear()
        with CSession() as session:
            articles = session.query(classes.Article).all()
            producers = session.query(classes.Producer).all()
            selected_producer = self.cb_producer_d.currentText()
            if selected_producer:
                for producer in producers:
                    if producer.name == selected_producer:
                        self.producerXY = producer.uid
                        print (self.producerXY)
                for article in articles:
                    if article.producer_uid == self.producerXY:
                        self.cb_article_d.addItem(article.name)
            else:
                for article in articles:    
                    self.cb_article_d.addItem(article.name)

    def set_combobox_device_user(self):
        """Fill User ComboBox for QR-Code readings"""
        self.cb_device_user.clear()
        self.cb_device_user.addItem("")
        with CSession() as session:
            users = session.query(classes.User).all()
            for user in users:
                self.cb_device_user.addItem(f"{user.uid} {str(user)}")

    def set_combobox_device_location(self):
        """Fill Location ComboBox for QR-Code readings"""
        self.cb_device_location.clear()
        self.cb_device_location.addItem("")
        with CSession() as session:
            locations = session.query(classes.Location).all()
            locations.sort(key=lambda location: str(location))
            for location in locations:
                self.cb_device_location.addItem(location.name)

    def set_combobox_user_d(self):
        """Fill User ComboBox for Device creation"""
        self.cb_user_d.clear()
        self.cb_user_d.addItem("")
        with CSession() as session:
            users = session.query(classes.User).all()
            for user in users:
                self.cb_user_d.addItem(f"{user.uid} {str(user)}")
    
    def set_combobox_user_admin(self):
        """Fill User ComboBox for User change"""
        self.cb_user_admin.clear()
        self.cb_user_admin.addItem("")
        with CSession() as session:
            users = session.query(classes.User).all()
            for user in users:
                self.cb_user_admin.addItem(f"{user.uid} {str(user)}")

    def reload_user_change(self):
        """Fill TextBoxes for User change"""
        with CSession() as session:
            users = session.query(classes.User).all()
            selected_user = self.cb_user_admin.currentText()
            if selected_user == "":
                self.in_name_admin.setText("")
                self.in_surname_admin.setText("")
                self.in_email_admin.setText("")  
                self.in_phone_admin.setText("")  
                return
            user_uid = int(selected_user.split(" ")[0])
            if user_uid == self.logged_in_user.uid:
                self.checkBox.setEnabled(False)
            else:
                self.checkBox.setEnabled(True)
            
            for user in users:
                if user.uid == user_uid:
                    self.in_name_admin.setText(user.name) # fill textEdits for UserChange
                    self.in_surname_admin.setText(user.surname)
                    self.in_email_admin.setText(user.e_mail)  
                    self.in_phone_admin.setText(str(user.phonenumber))
                    self.cb_location_u_admin.setCurrentIndex(user.location_uid)

                    if user.is_admin:    
                        self.checkBox.setCheckState(2)
                    else:
                        self.checkBox.setCheckState(0)  
                
    def set_phonenumber(self, str_):
        """Set reference PhoneNumber display on User creation tab
        to PhoneNumber represantation of str_
        Args:
            str_(str): str_ to try and interpret as PhoneNumber
        """
        if str_:
            try:
                text = str(classes.PhoneNumber(str_))
            except classes.PhoneNumber.NoNumberFoundWarning:
                text = "Es konnte keine Nummer erkannt werden. Empfohlene Syntax ist: Vorwahl Benutzernummer-Durchwahl"    
        else:
            text = "Bitte geben Sie Ihre Telefonnummer ein."
        self.out_phone.setText(text)
        self.out_phone_admin.setText(text)

    def b_user_login_click(self):
        """Login button click"""
        LoginDialog(self).exec()
        self.update_user_dependant()
        if self.logged_in_user:
            # logger.info(f"Logged in as {self.logged_in_user}") # already logged in login
            self.timeout = classes.Timeout(
                config["timeout"]*60, 
                lambda signal: signal.emit(True), 
                self.ui.b_user_logout.clicked)
            self.timeout.start()

    def b_user_logout_click(self, timed_out=False):
        """Logout button click - also handles timeouts via timed_out flag
        Args:
            timed_out(bool): Set to True to handle logout as one rooted in timeout
        """
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

        self.status_bar_text("Sie wurden wegen Inaktivität automatich ausgeloggt!", 5, "red")

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
            self.status_bar_text(f"Sie sind jetzt als {self.logged_in_user} angemeldet", 2, "green")

            self.in_name.setText(self.logged_in_user.name)
            self.in_surname.setText(self.logged_in_user.surname)
            self.in_email.setText(self.logged_in_user.e_mail)
            with CSession() as session:
                users = session.query(classes.User).all()
                userX = self.logged_in_user.name
                for user in users:
                    if user.name == userX:
                        self.in_phone.setText(str(user.phonenumber))
            
            if self.logged_in_user.is_admin:
                if self.ui.stackedWidget.currentIndex() == 4:
                    self.ui.stackedWidget.setCurrentIndex(3)
                
        else:
            self.ui.log_in_out.setCurrentIndex(0)
            self.label.setText("")
            if self.ui.stackedWidget.currentIndex() == 3:
                         self.ui.stackedWidget.setCurrentIndex(4)

    def mousePressEvent(self, QMouseEvent=None):
        """Event that's called on mouse click"""
        # print("Maus geklickt")
        self.mouseMoveEvent()
    
    def mouseMoveEvent(self, QMouseEvent=None):
        """Event that's called on mouse move"""
        """
        if QMouseEvent is not None:
            print("Maus bewegt")"""
        if hasattr(self, "timeout"):
            self.timeout.reset()

    def b_user_change_click(self):
        name = self.in_name.text()
        surname = self.in_surname.text()
        e_mail = self.in_email.text()
        phonenumber = self.in_phone.text()
        location = self.cb_location_u.currentText()
        password_1 = self.in_password1.text()
        password_2 = self.in_password2.text()
        if password_1 == "" and self.logged_in_user:
            password_1 = False # leave password as it
            password_2 = False

        locals_ = {key: value for (key, value) in locals().items() if key != "self"}
        if "" in locals_.values():
            self.not_all_fields_filled_notice()
            return
        
        if password_1 != password_2:       
            self.status_bar_text("Die Passwörter stimmen nicht überein", 5, "red")
            return
        else:
            password = password_1

        if self.logged_in_user:
            user = self.logged_in_user
        else:
            user = classes.User(e_mail, password)

        with CSession() as session:
            session.add(user)
            location = session.query(classes.Location).filter_by(name=location).first()
            user.name = name
            user.surname = surname
            user.e_mail = e_mail
            user.phonenumber = classes.PhoneNumber(phonenumber)
            user.location = location
            if self.logged_in_user and password:
                user.hash(password)
                
        if self.logged_in_user:
            self.logged_in_user = user
            logger.info(f"User {user} changed through UI")
            self.status_bar_text(f"Benutzer {user} wurde erfolgreich geändert", 5, "green")
        else:
            self.status_bar_text(f"Benutzer {user} wurde erfolgreich angelegt", 5, "green")
            logger.info(f"User {user} created through UI")

    def b_user_change_admin_click(self):
        user_to_change = self.cb_user_admin.currentText()
        name = self.in_name_admin.text()
        surname = self.in_surname_admin.text()
        e_mail = self.in_email_admin.text()
        phonenumber = self.in_phone_admin.text()
        location = self.cb_location_u_admin.currentText()
        locals_ = {key: value for (key, value) in locals().items() if key != "self"}
        if "" in locals_.values():
            self.not_all_fields_filled_notice()
            return

        user_to_change_uid = user_to_change.split(" ")[0]
        with CSession() as session:
            user = session.query(classes.User).filter_by(uid=user_to_change_uid).first()
            location = session.query(classes.Location).filter_by(name=location).first()
            user.name = name
            user.surname = surname
            user.e_mail = e_mail
            user.phonenumber = classes.PhoneNumber(phonenumber)
            user.location = location
            user.is_admin = self.checkBox.isChecked()
            session.add_all((user, location))
                   
        if self.logged_in_user.uid == user.uid:
            self.logged_in_user = user
        logger.info(f"User {user} changed through UI by admin {self.logged_in_user.uid}")
        self.status_bar_text(f"Benutzer {user} wurde erfolgreich geändert", 5, "green")
        
    def reset_password(self):
        """Set new password and salt for user, push it to db and show it in UI"""
        user_to_change = self.cb_user_admin.currentText()
        password = self.in_password_admin.text()
        if password == "":
            password = False # autogenerate password
        locals_ = {key: value for (key, value) in locals().items() if key != "self"}
        if "" in locals_.values():
            self.not_all_fields_filled_notice()
            return

        user_to_change_uid = user_to_change.split(" ")[0]
        with CSession() as session:
            user = session.query(classes.User).filter_by(uid=user_to_change_uid).first()
            session.add(user)
            if password:
                user.hash(password)
            else:
                password = slots.reset_password(user)

        self.in_password_admin.setText("")  
        messagebox = QtWidgets.QMessageBox()
        messagebox.setIcon(QtWidgets.QMessageBox.Information)
        messagebox.setWindowTitle(f"Neues Passwort für User {user.uid}")
        messagebox.setText(f"Das neue Passwort für {user} ist {password}")
        messagebox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        messagebox.exec_()

    def b_save_device_click(self):
        """Dialog to choose path for qr-codes"""
        qr_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Bitte wählen Sie ein Verzeichnis")
        if qr_path:
            self.t_path_device.setText(qr_path)

    def b_change_device_click(self):
        """Change Responsibility of a Device"""
        new_location = self.cb_device_location.currentText() # gives location.name
        new_user = self.cb_device_user.currentText()    # gives 'user.uid user.surname user.name'
        user_uid = int(new_user.split(" ")[0])
        device = int(self.t_code_device.text().split(" ")[-1])

        locals_ = {key: value for (key, value) in locals().items() if key != "self"}
        if "" in locals_.values():
            self.not_all_fields_filled_notice()
            return

        with CSession() as session:
            resp = session.query(classes.Responsibility).join(classes.Device).filter_by(uid=device).first()
            location = session.query(classes.Location).filter_by(name=new_location).first()
            user = session.query(classes.User).filter_by(uid=user_uid).first()
            if self.logged_in_user:
                if user.uid != self.logged_in_user.uid and not self.logged_in_user.is_admin:
                    self.status_bar_text("Um Geräte einem anderen Nutzer zuzuweisen ist ein Administrator nötig!", 5, "red")
                    return    
            else:
                self.status_bar_text("Um Geräte einem anderen Nutzer zuzuweisen ist ein Administrator nötig!", 5, "red")
                return
            resp.location = location
            resp.user = user
            logger.info(f"Modified Responsibility for Device {resp.device.uid}")
            self.status_bar_text(f"Verantwortlichkeit für Gerät {resp.device.uid} wurde bearbeitet", 5, "green")

    def b_delete_device_click(self):
        """Delete device from database"""
        device = int(self.t_code_device.text().split(" ")[-1])
        if device == "":
            self.not_all_fields_filled_notice()
            return
        if not self.logged_in_user:
            self.status_bar_text("Um Geräte zu löschen müssen Sie angemeldet sein", 5, "red")
            return
        with CSession() as session:
            resp = session.query(classes.Responsibility).join(classes.Device).filter_by(uid=device).first()
            session.delete(resp.device)
            session.delete(resp)
            logger.info(f"Deleted Device {resp.device.uid}")
            self.status_bar_text(f"Gerät {resp.device.uid} wurde aus der Datenbank entfernt", 5, "green")
            self.t_code_device.setText("")
            self.t_code_user.setText("")
            self.t_code_location.setText("")
            self.set_tree()

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
            if self.logged_in_user:
                if user.uid != self.logged_in_user.uid and not self.logged_in_user.is_admin:
                    self.status_bar_text("Um Geräte für einen anderen Nutzer zu erzeugen ist ein Administrator nötig!", 5, "red")
                    return
            else:
                self.status_bar_text("Um Geräte zu erzeugen müssen Sie eingeloggt sein", 5, "red")
                return  
            device = classes.Device()
            session.add(device)
            device.article = article
            resp = classes.Responsibility(device, user, location)
            session.add(resp)
        path = pathlib.Path(self.t_path_device.text())
        if not re.match(r".*\.(?P<filetype>.*$)", str(path), re.IGNORECASE):
            path /= utils.normalize_filename(f"{device.uid}_{device.article.name}.svg")
        if not utils.check_if_file_exists(path):
            self.status_bar_text(f"{path} ist kein gültiger Pfad/eine bereits vorhandene Datei", 5, "red")
            return
        try:
            generate_qr(device, path)
        except NotImplementedError as e:
            logger.error(str(e))
            self.status_bar_text(f"Um {e[1]} Dateien zu speichern sind weitere Pakete nötig. Das Standartformat ist svg", 10, "red")
        else:
            self.status_bar_text(f"Gerät erfolgreich angelegt. Der QR-Code wurde unter {path} gespeichert", 10, "green")





    def b_create_new_qrcode_click(self):
        """Creates a new QR-Code for a device"""
        device = self.ui.treeWidget.currentItem().text(0)
        device_uid = re.match(r"(?:.* mit ID )(?P<ID>\d+)$", device).group("ID")

        with CSession() as session:
            device = session.query(classes.Device).filter_by(uid=device_uid).first()
            filename = utils.normalize_filename(f"{device.uid}_{device.article.name}.svg")
            path = pathlib.Path(config["qr_path"])
            path /= filename
            if not utils.check_if_file_exists(path):
                self.status_bar_text(f"{path} ist kein gültiger Pfad/eine bereits vorhandene Datei", 5, "red")
                return
            try:
                generate_qr(device, path)
            except NotImplementedError as e:
                logger.error(str(e))
                self.status_bar_text(f"Um {e[1]} Dateien zu speichern sind weitere Pakete nötig. Das Standartformat ist svg", 10, "red")
            else:
                self.status_bar_text(f"Der QR-Code wurde unter {config['qr_path']} gespeichert", 8, "green")


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
            self.status_bar_text(f'Artikel mit Name "{name}" existiert bereits', 5, "red")
        else:
            self.status_bar_text(f'Artikel "{name}" wurde angelegt', 5, "green")
        self.t_name_a.setText("")
        self.set_combobox_article_d()

    def b_create_producer_click(self):
        name = self.t_name_p.text()
        try:
            slots.create_producer(name=name)
        except classes.IntegrityError as e:
            logger.info(str(e))
            self.status_bar_text(f'Produzent mit Namen "{name}" existiert bereits', 5, "red")
        else:
            self.status_bar_text(f'Produzent "{name}" wurde angelegt', 5, "green")
        self.t_name_p.setText("")
        self.set_combobox_producer_d()
        self.set_combobox_producer_a()

    def not_all_fields_filled_notice(self):
        """Show message that user hasn't filled all necessary fields
        This could also be reworked to use signals and slots
        """
        self.status_bar_text("Bitte füllen Sie alle Felder aus", 5, "red")

    def recognized_barcode(self, str_):
        """Slot that's called if the camera recognized a barcode"""
        logger.info(f"Recognized barcode: {str_}")
        try:
            match = re.search(r"id=(?P<id>\d+).*", str_)
            # Could also match on r"id=(?P<id>\d+).*name=(?P<name>.*)" to only recognize codes that contain name and uid
            uid = match.group("id")
        except AttributeError:
            logger.info("Tried scanning external code/code with wrong data")
            return
        with CSession() as session:
            resp = session.query(classes.Responsibility).join(classes.Device).filter_by(uid=uid).first()
            if resp is None:
                logger.info(f"Scanned device is not in Database {uid}")
                return
            self.t_code_device.setText(str(resp.device))
            self.t_code_user.setText(str(resp.user))
            self.t_code_location.setText(str(resp.location))
            self.status_bar_text("Barcode erkannt", 2, "green")
        logger.info("Successfully processed barcode")


class LoginDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None):
        path = utils.absolute_path("login.ui")
        super().__init__(parent)
        self.parent = parent
        self.ui = uic.loadUi(path, self)
        self.b_login.clicked.connect(self.b_login_click)
        self.b_password_lost.clicked.connect(self.b_password_lost_click)

    def b_login_click(self):
        username = self.t_username.text()
        password = self.t_password.text()
        try:
            self.parent.logged_in_user = slots.login(username, password)
        except ValueError:
            self.parent.status_bar_text(f'Benutzer "{username}" ist nicht bekannt', 5, "red")
        self.close()

    def b_password_lost_click(self):
        ResetDialog(self).exec()


class ResetDialog(QtWidgets.QDialog):        #Dialog to select a filepath for password reset
    filepath = ""
    def __init__(self, parent=None):
        path = utils.absolute_path("reset.ui")
        super().__init__(parent)
        self.parent = parent
        self.ui = uic.loadUi(path, self)
        self.b_browse.clicked.connect(self.b_browse_click)
        self.b_password_reset.clicked.connect(self.b_password_reset_click)
        self.b_password_close.clicked.connect(self.b_password_close_click)
        self.t_path.setText(self.filepath)
        self.ui.b_browse.setIcon(QtGui.QIcon("pictures/folder.png"))
        self.ui.b_browse.setIconSize(QtCore.QSize(20,20))
    
    def b_browse_click(self):
        self.filepath = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File')
        self.t_path.setText(self.filepath[0])

    def b_password_reset_click(self):
        user = self.t_user.text()
        path = self.t_path.text()
        if "" in (user, path):
            self.close()
            self.parent.parent.not_all_fields_filled_notice()
            ResetDialog(self.parent).exec()
            return

        private_path = pathlib.Path(path)
        public_path = keys.PUBLIC_KEY_PATH
        with CSession() as session:
            user = session.query(classes.User).filter_by(e_mail=user).first()
            session.add(user)
            if not user:
                self.parent.parent.status_bar_text("Unbekannter Benutzer!", 5, "red")
                return
            try:
                password = slots.reset_admin_password(user, public_path, private_path)
            except ValueError as e:
                logger.info(str(e))
                self.parent.parent.status_bar_text("Ungültiger Schlüssel!", 5, "red")
                return
            except FileNotFoundError as e:
                logger.info(str(e))
                self.parent.parent.status_bar_text(f"Keine gültige Datei unter {private_path}!", 5, "red")
                return
                
        messagebox = QtWidgets.QMessageBox()
        messagebox.setIcon(QtWidgets.QMessageBox.Information)
        messagebox.setWindowTitle(f"Neues Passwort für User {user.uid}")
        messagebox.setText(f"Das neue Passwort für {user} ist {password}")
        messagebox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        messagebox.exec_()

        self.close()
        self.parent.close()
        
    def b_password_close_click(self):
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog_main = MainDialog()
    dialog_login = LoginDialog()
    dialog_save = ResetDialog()

    dialog_main.show() # show dialog_main as modeless dialog => return control back immediately

    sys.exit(app.exec_())