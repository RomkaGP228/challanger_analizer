import sys
import sqlite3
from pathlib import PurePath
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QDialog, QTreeWidgetItem
import data.functions as funcs


class mainwindow_class(QMainWindow):
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
        path = PurePath('db/challenges.db')
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('SELECT challenge_lable, duration FROM challenges')
        for i in cursor.fetchall():
            res = QTreeWidgetItem(i)
            self.treeWidget.insertTopLevelItem(0, res)

    def run(self):
        self.dayswindow_class_ex.show()

    def create_new_one(self):
        self.add_new_one_class_ex.show()

    def updater(self):
        path = PurePath('db/challenges.db')
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('SELECT challenge_lable, duration FROM challenges')
        self.treeWidget.insertTopLevelItem(0, QTreeWidgetItem(cursor.fetchall()[-1]))


class dayswindow_class(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('forms/days_challenger.ui', self)


class add_new_one_class(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('forms/creating_window_challenger.ui', self)
        # тут идет подключение кнопок
        self.create_button.clicked.connect(self.adder)

    def adder(self):
        if funcs.add_new_one_challenge_func(self.name_enter.text(), self.duration_enter.text()):
            self.close()
