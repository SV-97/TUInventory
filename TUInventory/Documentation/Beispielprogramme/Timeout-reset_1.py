def mouseMoveEvent(self, QMouseEvent):
    if "timeout" in self.__dict__:
        self.timeout.reset()

""" ca. 100 Elemente
{'b_home_1': <PyQt5.QtWidgets.QCommandLinkButton object at 0x7f48a0c9da68>,
 'b_search_places': <PyQt5.QtWidgets.QPushButton object at 0x7f4898283798>,
    [...]
 'ui': <__main__.MainDialog object at 0x7f48a17f3948>,
 'videoFeed': <PyQt5.QtWidgets.QLabel object at 0x7f4898283948>}
 """