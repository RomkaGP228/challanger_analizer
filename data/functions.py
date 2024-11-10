import datetime as dt
import sqlite3
import pathlib
import json
from PyQt6.QtWidgets import QMessageBox


def add_new_db():
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
    # подключение БД
    path = pathlib.Path('db/challenges.db').absolute()
    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    # исключение с созданным файлы
    cursor.execute('SELECT challenge_lable FROM challenges')
    db_data = cursor.fetchall()
    print(duration, type(duration))
    try:
        if len(db_data) > 0:
            if len([*filter(lambda x: title == x[0], db_data)]) > 0:
                raise ValueError('Челлендж с таким именем уже существует')
    except ValueError as e:
        show_error_message('error', f'{e}')
        return False

    # исключаем пробел
    try:
        if title == '':
            raise ValueError('Введите что-либо в поле названия')
    except ValueError as e:
        show_error_message('error', f'{e}')
        return False

    # исключение если длительность не число
    try:
        if duration.isdigit() is False:
            raise ValueError('Длительность не целочисленное')
        else:
            if int(duration) < 1:
                raise ValueError('Длительность меньше 1')
            else:
                if int(duration) > 3650:
                    raise ValueError('Пожалуйста, введите число меньше 3650')
    except ValueError as e:
        show_error_message('error', f'{e}')
        return False

    # тут идет создание json файла с названием самого челленджа
    day_today = dt.date.today()
    day_of_the_end = day_today + dt.timedelta(days=int(duration))
    with open(pathlib.Path(f'data/json_files/{title}.json').absolute(), mode='w') as new_json:
        competed = {i: [] for i in range(1, int(duration) + 1)}
        for i, v in enumerate(competed.values()):
            v.extend([(day_today + dt.timedelta(days=int(i))).strftime("%B %d, %Y"), 'X', ''])
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
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Icon.Critical)  # Устанавливаем иконку критической ошибки
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()
