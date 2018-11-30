import itertools
import os
import sys
import pathlib
import random
import sqlite3
import pprint

from PyQt5 import uic, QtWidgets, QtGui
import PyQt5.QtCore

connection_users = sqlite3.connect("tuinventory.db")

pp = pprint.PrettyPrinter()
def absolute_path(relative_path):
    path = pathlib.Path(os.path.dirname(__file__))
    return path / relative_path

locations = 10
users_per_location = 15
devices = itertools.count()
data = {f"Location{i}": {f"user{j}": [str(next(devices)) for k in range(random.randint(1,6))] for j in range(users_per_location)} for i in range(locations) }

pp.pprint(data)
class MainDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        path = absolute_path("DynamicResponsibility.ui")
        super().__init__(parent)
        self.ui = uic.loadUi(path, self)
        locations = [QtWidgets.QTreeWidgetItem([location]) for location in data]
        """
        for location in data:
            item = QtWidgets.QTreeWidgetItem([location])
            self.treeWidget.addTopLevelItem(item)
        """
        for location in locations:
            users = [QtWidgets.QTreeWidgetItem([child]) for child in data[location.text(0)].keys()]
            for user in users:
                devices = [QtWidgets.QTreeWidgetItem([device]) for device in data[location.text(0)][user.text(0)]]
                user.addChildren(devices)
            location.addChildren(users)
        self.treeWidget.addTopLevelItems(locations)


app = QtWidgets.QApplication(sys.argv)
dialog_main = MainDialog()
dialog_main.show() # show dialog_main as modeless dialog => return control back immediately

#pp.pprint(dialog_main.__dict__)
sys.exit(app.exec_())