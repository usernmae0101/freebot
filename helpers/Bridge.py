from PySide2.QtCore import QObject, QThread

from freebitcoin.User import User


class Bridge(QObject):
    def __init__(self, widget, index, login, password, proxy, key):
        QObject.__init__(self)

        self.thread = QThread()
        self.user = User(index, login, password, proxy, key)
        self.user.moveToThread(self.thread)
        self.init_signal_connections(widget)
        self.thread.started.connect(self.user.run)
        self.thread.start()

    def init_signal_connections(self, widget):
        self.user.signal_update_column_color.connect(widget.change_column_color)
        self.user.signal_update_column_text.connect(widget.change_column_text)
        self.user.signal_update_chart.connect(widget.update_chart)