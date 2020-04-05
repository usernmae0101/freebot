from PySide2.QtCore import Slot, Qt, QDateTime, QSettings
from PySide2.QtGui import QPainter, QColor
from PySide2.QtCharts import QtCharts
from PySide2.QtWidgets import (QWidget, QTableWidget, QHBoxLayout, QTableWidgetItem,
                               QHeaderView, QLineEdit, QVBoxLayout, QPushButton)
from time import time                               
from ast import literal_eval

from helpers import CONSTANTS
from helpers.Bridge import Bridge


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.row = 0
        self.coins_sum = 0
        self.settings = QSettings('NoneCompany', 'freebot')

        VBoxLayout = QVBoxLayout() # Right
        HBoxLayout = QHBoxLayout() # Left
        
        self.create_form()
        self.set_placeholders()
        self.define_table()
        
        FormLayout = QHBoxLayout()
        FormLayout.addWidget(self.form_login)
        FormLayout.addWidget(self.form_password)
        FormLayout.addWidget(self.form_proxy)
        
        self.create_buttons()
        FromButtonsLayout = QHBoxLayout()
        FromButtonsLayout.addWidget(self.add_button)
        FromButtonsLayout.addWidget(self.clear_button)

        self.series = QtCharts.QLineSeries()
        self.chart_view = QtCharts.QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        VBoxLayout.addWidget(self.form_key)
        VBoxLayout.addLayout(FormLayout)
        VBoxLayout.addLayout(FromButtonsLayout)
        VBoxLayout.addWidget(self.chart_view)
        VBoxLayout.addWidget(self.start_button)

        HBoxLayout.addWidget(self.table)
        HBoxLayout.addLayout(VBoxLayout)
        self.setLayout(HBoxLayout)

        self.update_chart([time(), 0], True)
        self.create_connections()

    def set_placeholders(self):
        self.form_login.setPlaceholderText('login')
        self.form_password.setPlaceholderText('password')
        self.form_proxy.setPlaceholderText('proxy')
        self.form_key.setPlaceholderText('API-key rucaptcha.com')

    def create_form(self):
        self.form_login = QLineEdit()
        self.form_password = QLineEdit()
        self.form_proxy = QLineEdit()
        self.form_key = QLineEdit()

    def create_buttons(self):
        self.add_button = QPushButton('add')
        self.clear_button = QPushButton('clear')
        self.start_button = QPushButton('start')

    def create_connections(self):
        self.add_button.clicked.connect(self.fillin_table)
        self.start_button.clicked.connect(self.init_threads)
        self.clear_button.clicked.connect(self.clear_table)

    def define_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(CONSTANTS.TABLE_COLUMNS))
        self.table.setHorizontalHeaderLabels(CONSTANTS.TABLE_COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        if self.settings.contains('key'):
            self.form_key.setText( self.get_settings('key') )

        if self.settings.contains('table'):
            for row in literal_eval(self.get_settings('table')):
                self.add_account(*row, False)

    def set_settings(self, key, value):
        if key == 'table':
            if self.settings.contains('table'):
                table = literal_eval(self.get_settings('table'))
                table.append(value)
                value = table
            else:
                value = [value]    

        self.settings.setValue(key, str(value))

    def get_settings(self, key):
        return self.settings.value(key)    

    @Slot(int, list)
    def change_column_color(self, row, RGB):
        for col in range( len(CONSTANTS.TABLE_COLUMNS) ):
            self.table.item(row, col).setBackground(QColor(*RGB))

    @Slot(int, str)
    def change_column_text(self, row, text):
        self.table.item(row, 3).setText(text)

    @Slot()
    def clear_table(self):
        self.settings.clear()
        self.table.setRowCount(0)
        self.row = 0

    @Slot()
    def fillin_table(self, settings=False):
        if self.check_form_state():
            return

        self.add_account(self.form_login.text(), 
                         self.form_password.text(),
                         self.form_proxy.text())
        
        self.form_login.clear()
        self.form_proxy.clear()
        self.form_password.clear()

    @Slot(list)
    def update_chart(self, data, init=False):
        self.coins_sum += data[1]

        MStime_now = float(QDateTime.currentDateTime().toMSecsSinceEpoch())

        if init:
            self.series.append(MStime_now, self.coins_sum)
            for i in range(6):
                if i and not i % 2:
                    self.series.append(MStime_now + (i * 1), self.coins_sum)
                else:
                    self.series.append(MStime_now + (i * 1), 0.00000001)
        else:    
            self.series.append(MStime_now, self.coins_sum)

        chart = QtCharts.QChart()
        chart.addSeries(self.series)
        if not init:
            chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        chart.setTitle('Progress')

        axisX = QtCharts.QDateTimeAxis()
        axisX.setTickCount(5)
        axisX.setFormat('HH:mm:ss')
        axisX.setTitleText('time')
        chart.addAxis(axisX, Qt.AlignBottom)
        self.series.attachAxis(axisX)

        axisY = QtCharts.QValueAxis()
        axisY.setTickCount(5)
        axisY.setLabelFormat('%.8f')
        axisY.setTitleText('coins')
        chart.addAxis(axisY, Qt.AlignLeft)
        self.series.attachAxis(axisY)

        self.chart_view.setChart(chart)

    @Slot()
    def init_threads(self):
        self.start_button.setEnabled(False)
        self.set_settings('key', self.form_key.text())

        self.threads = [Bridge(self, row,
                               self.table.item(row, 0).text(),
                               self.table.item(row, 1).text(),
                               self.table.item(row, 2).text(),
                               self.form_key.text()) 
                        for row in range(self.table.rowCount())]
        
    def check_form_state(self):
        return not self.form_login.text() \
        or not self.form_password.text() \
        or not self.form_proxy.text()

    def add_account(self, login, password, proxy, record=True):
        self.table.insertRow(self.row)

        self.table.setItem(self.row, 0, QTableWidgetItem(login))
        self.table.setItem(self.row, 1, QTableWidgetItem(password))
        self.table.setItem(self.row, 2, QTableWidgetItem(proxy))
        self.table.setItem(self.row, 3, QTableWidgetItem('?'))

        if record:
            self.set_settings('key', self.form_key.text())
            self.set_settings('table', [login, password, proxy])

        self.row += 1