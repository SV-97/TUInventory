
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen
from PyQt5.QtCore import Qt

def blue_white(dialog):
    dialog.setAutoFillBackground(True)
    p = dialog.palette()
    p.setColor(dialog.backgroundRole(), Qt.white)
    dialog.setPalette(p)