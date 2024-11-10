import pathlib
import sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QDialog, QTreeWidgetItem, QTableWidgetItem, QComboBox, QMessageBox, \
    QWidgetAction
import data.functions as funcs
from PyQt6.QtCore import pyqtSignal
import json


class MainWindowClass(QMainWindow):
    def __init__(self, add_new_one_class_ex):
        super().__init__()
        uic.loadUi('forms/start_window_challenger.ui', self)

        # тут идет инициализация созданных клонов методов классов
        self.add_new_one_class_ex = add_new_one_class_ex

        self.connection = sqlite3.connect(pathlib.Path('db/challenges.db').absolute())

        # тут идет подключение кнопок
        self.treeWidget.itemDoubleClicked.connect(self.show_info_about_challenge)
        self.Add_new_one.clicked.connect(self.create_new_one)
        self.delete_one.clicked.connect(self.delete_challenge)

        # добавление в sql таблицу
        self.load_challenges()

    def load_challenges(self):
        # загрузка всех челленджей из скльюэль в тривиджет
        cursor = self.connection.cursor()
        cursor.execute('SELECT challenge_lable, duration, completed FROM challenges')
        for i in cursor.fetchall():
            res = QTreeWidgetItem(i)
            self.treeWidget.insertTopLevelItem(0, res)

    def show_info_about_challenge(self, item, column):
        # метод для открытия информции о челлендже
        # создает новый экземпляр класса и передает туда информцию о челлендже с помощью json-файла
        self.DWC = DaysWindowClass(item.text(0), column)
        self.DWC.show()

    def create_new_one(self):
        self.add_new_one_class_ex.new_challenge_added.connect(self.updater)
        self.add_new_one_class_ex.show()

    def updater(self):
        # очистка тривиджета для добавление новой информации после добавления
        self.treeWidget.clear()
        self.load_challenges()

    def delete_challenge(self):
        # ДОБАВИТЬ УДАЛЕНИЕ ЭЛЕМЕНТОВ

        try:
            item = self.treeWidget.selectedItems()[0].text(0)
            valid = QMessageBox.question(self, '', f'Действительно удалить элемент с названием {item}',
                                         buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if valid == QMessageBox.StandardButton.Yes:
                cursor = self.connection.cursor()
                cursor.execute("""DELETE FROM challenges WHERE challenge_lable=?""", (item,))
                self.connection.commit()
                fil = pathlib.Path(f'data/json_files/{item}.json').absolute()
                fil.unlink()
                self.updater()
        except IndexError:
            funcs.show_error_message('error', 'Выберите челлендж из списка')


class DaysWindowClass(QMainWindow):
    def __init__(self, name, column):
        super().__init__()
        uic.loadUi('forms/days_challenger.ui', self)
        # все связаное с таблицей
        self.name = name
        self.column = column
        self.load_info_about_challenge()
        # добавляем и инициализируем кнопочки
        self.pushButton.clicked.connect(self.update_json)
        self.self_close.clicked.connect(self.close)
        # связаное с закрытием и тд
        QWidgetAction(self).triggered.connect(self.closeEvent)

    def load_info_about_challenge(self):
        with open(pathlib.Path(f'data/json_files/{self.name}.json').absolute(), mode='r') as in_json_f:
            self.show()
            json_data_about_challenge = [json.load(in_json_f)]
            self.tableWidget.setRowCount(len(*json_data_about_challenge))
            for i in json_data_about_challenge:
                for row, (k, v) in enumerate(i.items()):
                    info_about_class = [k]
                    info_about_class.extend(v)
                    for col, val in enumerate(info_about_class):
                        if col == 2:
                            button = QComboBox()
                            button.addItems(['X', 'V'])
                            button.setCurrentText(val)
                            self.tableWidget.setCellWidget(row, col, button)
                        else:
                            res = QTableWidgetItem(val)
                            self.tableWidget.setItem(row, col, res)
            in_json_f.close()

    def update_json(self):
        data = {}
        for row in range(self.tableWidget.rowCount()):
            row_data = []
            for col in range(self.tableWidget.columnCount()):
                if col == 2:
                    item = self.tableWidget.cellWidget(row, col)
                    row_data.append(item.currentText())
                else:
                    item = self.tableWidget.item(row, col)
                    row_data.append(item.text())
            data[row+1] = row_data[1:]
            with open(pathlib.Path(f'data/json_files/{self.name}.json').absolute(), mode='w') as json_file_to_update:
                json.dump(data, json_file_to_update)
                json_file_to_update.close()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Подтверждение выхода', 'Вы уверены, что хотите выйти без сохранения?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()  # Закрываем окно
        else:
            event.ignore()


class AddNewOneClass(QDialog):
    new_challenge_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi('forms/creating_window_challenger.ui', self)
        # тут идет подключение кнопок
        self.create_button.clicked.connect(self.adder)

    def adder(self):
        a = funcs.add_new_one_challenge_func(self.name_enter.text(), self.duration_enter.text())
        if not a:
            return
        self.name_enter.clear()
        self.duration_enter.clear()
        self.close()
        self.new_challenge_added.emit()
