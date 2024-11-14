import datetime as dt
import sqlite3
import pathlib
import json
from PyQt6.QtWidgets import QMessageBox


def add_new_db():
    # функция, которая создает новую бд, если ее нет, запускается она каждый раз при запуске
    path = pathlib.Path('db/challenges.db').absolute()
    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS challenges(
       challenge_lable TEXT,
       datefrom TEXT,
       dateto TEXT,
       duration TEXT,
       completed TEXT,
       info TEXT);
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS challenge_index ON challenges (challenge_lable)')
    connection.commit()
    connection.close()


def add_new_one_challenge_func(title, duration, complited='0'):
    # функция, которая создает новый челлендж, добавляет его в бд и создает файл json
    # подключение БД
    path = pathlib.Path('db/challenges.db').absolute()
    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    # исключение с созданным файлы
    cursor.execute('SELECT challenge_lable FROM challenges')
    db_data = cursor.fetchall()
    try:
        if len(db_data) > 0:
            if len([*filter(lambda x: title == x[0], db_data)]) > 0:
                raise ValueError('Челлендж с таким именем уже существует')
    except ValueError as e:
        show_error_message('error', f'{e}')
        return False

    # исключаем пробел
    try:
        if title == '' or title.isspace():
            raise ValueError('Введите что-либо в поле названия')
    except ValueError as e:
        show_error_message('error', f'{e}')
        return False

    # исключение если длительность не число
    try:
        if (duration.isdigit() is False) or duration[0] == '0':
            raise ValueError('Длительность не целочисленное')
        else:
            if int(duration) > 1825:
                raise ValueError('Пожалуйста, введите число меньше 1825')
    except ValueError as e:
        show_error_message('error', f'{e}')
        return False

    # тут идет создание json файла с названием самого челленджа
    day_today = dt.date.today()
    day_of_the_end = day_today + dt.timedelta(days=int(duration))
    with open(pathlib.Path(f'json_files/{title}.json').absolute(), mode='w') as new_json:
        competed = {i: [] for i in range(1, int(duration) + 1)}
        for i, v in enumerate(competed.values()):
            v.extend([(day_today + dt.timedelta(days=int(i))).strftime("%d %B, %Y"), 'X', ''])
        json.dump(competed, new_json)
        new_json.close()

    # Добавляем нового пользователя
    cursor.execute(
        'INSERT INTO challenges (challenge_lable, datefrom, dateto, duration, completed, info) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        (title, day_today, day_of_the_end, duration, complited, f'{title}.json'))

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
    return True


def show_error_message(title, message):
    # функция для показа MessageBox с ошибкой
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Icon.Critical)  # Устанавливаем иконку критической ошибки
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


def show_ask_message(parent, title, message):
    # функция, которая показывает Messagebox вопрос
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    return msg_box.exec()


def delete_challenge(item):
    # функция для удления челленжа из базы данных и его json файла
    connection = sqlite3.connect(pathlib.Path('db/challenges.db').absolute())
    cursor = connection.cursor()
    cursor.execute("""DELETE FROM challenges WHERE challenge_lable=?""", (item,))
    connection.commit()
    fil = pathlib.Path(f'json_files/{item}.json').absolute()
    fil.unlink()
