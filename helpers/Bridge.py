from PySide2.QtCore import QObject, QThread

from freebitcoin.User import User


class Bridge(QObject):
    def __init__(self, widget, index, login, password, key):
        QObject.__init__(self)

        self.thread = QThread()
        self.user = User(index, login, password, key)
        self.user.moveToThread(self.thread)
        self.user.signal_update_column_color.connect(widget.change_column_color)
        self.user.signal_update_column_text.connect(widget.change_column_text)
        self.user.signal_update_chart.connect(widget.update_chart)
        self.thread.started.connect(self.user.run)
        self.thread.start()