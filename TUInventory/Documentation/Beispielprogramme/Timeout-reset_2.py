def mouseMoveEvent(self, QMouseEvent):
    if hasattr(self, "timeout"):
        self.timeout.reset()