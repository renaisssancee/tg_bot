import sqlite3

def create_tables():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    # Создание таблицы расписания
    cursor.execute('''CREATE TABLE IF NOT EXISTS timetable
                      (DateTime TEXT, Master TEXT)''')

    # Создание таблицы информации
    cursor.execute('''CREATE TABLE IF NOT EXISTS info
                      (Service TEXT, Info TEXT, Time TEXT, Price TEXT)''')
    
    # Создание таблицы записей
    cursor.execute('''CREATE TABLE IF NOT EXISTS appointments
                      (id INTEGER, master_name TEXT, time_slot TEXT, user_name TEXT, phone_number TEXT, procedure TEXT, status TEXT DEFAULT 'pending')''')

    connection.commit()
    connection.close()
