import sys
import sqlite3
from pathlib import PurePath
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QDialog, QTreeWidgetItem
import data.functions as funcs
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMessageBox


class main_window_class(QMainWindow):
    def __init__(self, add_new_one_class_ex, dayswindow_class_ex):
        super().__init__()
        uic.loadUi('forms/start_window_challenger.ui', self)

        # тут идет инициализация созданных клонов методов классов
        self.add_new_one_class_ex = add_new_one_class_ex
        self.dayswindow_class_ex = dayswindow_class_ex

        # тут идет подключение кнопок
        self.treeWidget.clicked.connect(self.run)
        self.Add_new_one.clicked.connect(self.create_new_one)

        # добавление в sql таблицу
        self.load_challenges()

    def load_challenges(self):
        path = PurePath('db/challenges.db')
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('SELECT challenge_lable, duration FROM challenges')
        for i in cursor.fetchall():
            res = QTreeWidgetItem(i)
            self.treeWidget.insertTopLevelItem(0, res)

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

    def run(self):
        self.dayswindow_class_ex.show()

    def create_new_one(self):
        self.add_new_one_class_ex.new_challenge_added.connect(self.updater)  # Подключение сигнала
        self.add_new_one_class_ex.show()

    def updater(self):
        self.treeWidget.clear()
        self.load_challenges()


class dayswindow_class(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('forms/days_challenger.ui', self)


class add_new_one_class(QDialog):
    new_challenge_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi('forms/creating_window_challenger.ui', self)
        # тут идет подключение кнопок
        self.create_button.clicked.connect(self.adder)

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Critical)  # Устанавливаем иконку критической ошибки
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def adder(self):
        a = funcs.add_new_one_challenge_func(self.name_enter.text(), self.duration_enter.text(), self)
        if not a:
            return
        self.name_enter.clear()
        self.duration_enter.clear()
        self.close()
        self.new_challenge_added.emit()
