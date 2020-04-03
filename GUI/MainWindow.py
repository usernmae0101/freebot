from PySide2.QtWidgets import QMainWindow
from PySide2.QtCore import qApp

from helpers import CONSTANTS
from GUI.Widget import Widget


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.init_UI()
        
        widget = Widget()
        self.setCentralWidget(widget)

    def init_UI(self):
        geometry = qApp.desktop().availableGeometry(self)
        self.resize(geometry.width() * 0.8, geometry.height() * 0.56) 
        self.setWindowTitle(f'{CONSTANTS.APP_NAME} {CONSTANTS.APP_VERSION}')
