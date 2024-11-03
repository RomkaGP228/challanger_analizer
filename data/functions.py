import datetime as dt
import sqlite3
from pathlib import PurePath
import json


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
       info TEXT);
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS challenge_index ON challenges (challenge_lable)')
    connection.commit()
    connection.close()


def add_new_one_challenge_func(title, duration, complited=0):
    path = PurePath('db/challenges.db')
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    day_today = dt.date.today()
    day_of_the_end = day_today + dt.timedelta(days=int(duration))
    # тут идет создание json файла с названием самого челленджа
    # ДОПИСАТЬ ОШИБКУ ЧТО УЖЕ ТАКОЕ СУЩЕСТВУЕТ
    with open(PurePath(f'data/{title}.json'), mode='w') as new_json:
        competed = {i: [] for i in range(1, int(duration) + 1)}
        for i, v in enumerate(competed.values()):
            v.extend([(day_today + dt.timedelta(days=int(i))).strftime("%B %d, %Y"), 'X'])
        json.dump(competed, new_json)
    # Добавляем нового пользователя
    cursor.execute('INSERT INTO challenges (challenge_lable, datefrom, dateto, duration, info) VALUES (?, ?, ?, ?, ?)',
                   (title, day_today, day_of_the_end, duration, f'{title}.json'))

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
    return True


def add_complited_challenge_func(name):
    pass
