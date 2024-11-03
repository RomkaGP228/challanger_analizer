import datetime as dt
import sqlite3
from pathlib import PurePath
import json
from PyQt6.QtWidgets import QMessageBox


def add_new_db():
    path = PurePath('db/challenges.db')
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


def add_new_one_challenge_func(title, duration, self, complited='0'):
    # подключение БД
    path = PurePath('db/challenges.db')
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
        self.show_error_message('error', f'{e}')
        return False

    # исключаем пробел
    try:
        if title == '':
            raise ValueError('Введите что-либо в поле названия')
    except ValueError as e:
        self.show_error_message('error', f'{e}')
        return False

    # исключение если длительность не число
    try:
        if duration.isdigit() is False:
            raise ValueError('Длительность не целочисленное')
    except ValueError as e:
        self.show_error_message('error', f'{e}')
        return False

    # тут идет создание json файла с названием самого челленджа
    day_today = dt.date.today()
    day_of_the_end = day_today + dt.timedelta(days=int(duration))
    with open(PurePath(f'data/json_files/{title}.json'), mode='w') as new_json:
        competed = {i: [] for i in range(1, int(duration) + 1)}
        for i, v in enumerate(competed.values()):
            v.extend([(day_today + dt.timedelta(days=int(i))).strftime("%B %d, %Y"), 'X'])
        json.dump(competed, new_json)

    # Добавляем нового пользователя
    cursor.execute('INSERT INTO challenges (challenge_lable, datefrom, dateto, duration, completed, info) VALUES (?, ?, ?, ?, ?, ?)',
                   (title, day_today, day_of_the_end, duration, complited, f'{title}.json'))

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
    return True


