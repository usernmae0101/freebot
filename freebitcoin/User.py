from PySide2.QtCore import QObject, Signal
from time import sleep, time

from freebitcoin.API import API
from helpers.RucaptchaAPI import RucaptchaAPI


class User(QObject):
    signal_update_column_color = Signal(int, list)
    signal_update_column_text = Signal(int, str)
    signal_update_chart = Signal(list)

    def __init__(self, index, login, password, key):
        QObject.__init__(self)

        self.key = key
        self.index = index
        self.login = login
        self.password = password

    def alert_user(self, success):
        self.signal_update_column_color.emit(self.index, [20, 200, 20] if success else [200, 20, 20])       

    def update_chart(self, coins):
        self.signal_update_chart.emit([time(), float(coins)])

    def update_balance(self, balance):
        self.signal_update_column_text.emit(self.index, balance)

    def run(self):
        try:
            self.api = API(self.login, self.password, self.key)
            self.update_balance( self.api.parse_coins() )
            self.alert_user(True)
            
            while True:
                sleep(3600)
        except Exception as msg:
            self.alert_user(False)