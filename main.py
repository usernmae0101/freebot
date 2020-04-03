import sys

from PySide2.QtWidgets import QApplication

from freebitcoin.API import API
from GUI.MainWindow import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())