import pathlib
import sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QDialog, QTreeWidgetItem, QTableWidgetItem, QComboBox, QMessageBox, \
    QWidgetAction, QTextEdit
import data.functions as funcs
from PyQt6.QtCore import pyqtSignal
import json


class MainWindowClass(QMainWindow):
    def __init__(self, add_new_one_class_ex):
        """Этот класс отвечает за основное окно, где происходит взаимодествие со всеми челленджами"""
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
        data = cursor.fetchall()
        for i in data:
            with open(f'json_files/{i[0]}.json', mode='r') as in_json_f:
                info_about_completed = len([*filter(lambda v: v[1] == 'V', json.load(in_json_f).values())])
            in_json_f.close()
            # i[-1] = str(info_about_completed)
            res = QTreeWidgetItem([*list(i[0:2]), str(info_about_completed)])
            self.treeWidget.insertTopLevelItem(0, res)

    def show_info_about_challenge(self, item, column):
        # метод для открытия информции о челлендже
        # создает новый экземпляр класса и передает туда информцию о челлендже с помощью json-файла
        self.DWC = DaysWindowClass(item.text(0), column)
        self.DWC.info_challenge_update.connect(self.updater)
        self.DWC.info_challenge_update.connect(self.ask_delete)
        self.DWC.show()

    def create_new_one(self):
        # этот метод отвечает за создание нового челленжа, а конкретно за обновление информации в оснвном окне
        self.add_new_one_class_ex.new_challenge_added.connect(self.updater)
        self.add_new_one_class_ex.show()

    def updater(self):
        # очистка тривиджета для добавление новой информации после добавления
        self.treeWidget.clear()
        self.load_challenges()

    def delete_challenge(self):
        # этот метод отвечает за удаление чедденжа из основного окна, sql таблици и json файла с таким именем
        try:
            item = self.treeWidget.selectedItems()[0].text(0)
            valid = funcs.show_ask_message(self, '', f'Действительно удалить элемент с названием {item}')
            if valid == QMessageBox.StandardButton.Yes:
                funcs.delete_challenge(item)
                self.updater()
        except IndexError:
            funcs.show_error_message('error', 'Выберите челлендж из списка')

    def ask_delete(self):
        print('yws')
        for row in range(self.treeWidget.topLevelItemCount()):
            challenge = self.treeWidget.topLevelItem(row)
            if challenge.text(1) == challenge.text(2):
                ask = funcs.show_ask_message(self, 'Вопрос', f"""Не хотите ли вы удалить
челленж с названием: {challenge.text(0)}?\nПричина: Выполнен""")
                if ask == QMessageBox.StandardButton.Yes:
                    # self.delete_challenge(challenge.text(0))
                    funcs.delete_challenge(challenge.text(0))
                    self.updater()
                    self.DWC.destroy()
                    break


class DaysWindowClass(QMainWindow):
    info_challenge_update = pyqtSignal()

    def __init__(self, name, column):
        """Этот класс отвечает за окно с информацией о челлендже."""
        super().__init__()
        uic.loadUi('forms/days_challenger.ui', self)
        # все связаное с таблицей
        self.name = name
        self.setWindowTitle(self.name)
        self.column = column
        self.load_info_about_challenge()
        # добавляем и инициализируем кнопочки
        self.pushButton.clicked.connect(self.update_json)
        self.self_close.clicked.connect(self.closer)
        # связаное с закрытием и тд
        QWidgetAction(self).triggered.connect(self.closeEven)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(3, 300)

    def load_info_about_challenge(self):
        # Этот метод отвечает за загрузку информации о челлендже из json файла
        with (open(pathlib.Path(f'json_files/{self.name}.json').absolute(), mode='r') as in_json_f):
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
                        elif col == 3:
                            text_browser = QTextEdit()
                            text_browser.setText(val)
                            self.tableWidget.setCellWidget(row, col, text_browser)
                        else:
                            res = QTableWidgetItem(val)
                            self.tableWidget.setItem(row, col, res)
            in_json_f.close()

    def update_json(self):
        # Этот класс отвечает за обновление json файла после внесения изменений пользователем через это окно
        data = {}
        for row in range(self.tableWidget.rowCount()):
            row_data = []
            for col in range(self.tableWidget.columnCount()):
                if col == 2:
                    item = self.tableWidget.cellWidget(row, col)
                    row_data.append(item.currentText())
                elif col == 3:
                    item = self.tableWidget.cellWidget(row, col)
                    row_data.append(item.toPlainText())
                else:
                    item = self.tableWidget.item(row, col)
                    row_data.append(item.text())
            data[row + 1] = row_data[1:]
            with open(pathlib.Path(f'json_files/{self.name}.json').absolute(), mode='w') as json_file_to_update:
                json.dump(data, json_file_to_update)
                json_file_to_update.close()
        self.info_challenge_update.emit()
        self.destroy()

    def closeEvent(self, event):
        # Этот метод отвечает за диалоговое окно с вопросом, уверен ли пользователь в выходе
        reply = funcs.show_ask_message(self, 'Подтверждение выхода', 'Вы уверены, что хотите выйти?')

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()  # Закрываем окно
        else:
            event.ignore()

    def closer(self):
        self.destroy()


class AddNewOneClass(QDialog):
    new_challenge_added = pyqtSignal()

    def __init__(self):
        """Этот класс отвечает за добавление нового челленжа"""
        super().__init__()
        uic.loadUi('forms/creating_window_challenger.ui', self)
        # тут идет подключение кнопок
        self.create_button.clicked.connect(self.adder)
        self.setWindowTitle('Add New One')

    def adder(self):
        # этот метод отвечает за добавление нового челленжа
        # он передает информацию в функцию для создания нового челленжа
        a = funcs.add_new_one_challenge_func(self.name_enter.text(), self.duration_enter.text())
        if not a:
            return
        self.name_enter.clear()
        self.duration_enter.clear()
        self.close()
        self.new_challenge_added.emit()
