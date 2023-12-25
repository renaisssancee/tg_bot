import sqlite3

def get_available_times(master):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT DateTime FROM timetable WHERE Master = ?', (master,))
    scheduled_times = [row[0] for row in cursor.fetchall()]
    connection.close()
    return [time for time in scheduled_times]

# добавить доступное время для записи
def add_timetable(date_time, master):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO timetable (DateTime, Master) 
        SELECT ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM timetable 
            WHERE DateTime = ? AND Master = ?
        )
    """, (date_time, master, date_time, master))

    connection.commit()
    connection.close()


add_timetable('25.12.2023 11:00', 'Анна')
add_timetable('26.12.2023 12:00', 'Анна')
add_timetable('27.12.2023 13:00', 'Алина')
add_timetable('28.12.2023 14:00', 'Алина')
add_timetable('29.12.2023 15:00', 'Полина')
add_timetable('30.12.2023 16:00', 'Полина')
add_timetable('03.01.2024 15:00', 'Жанна')
add_timetable('04.01.2024 16:00', 'Жанна')


def remove_old_timetable_entries():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM info')
    connection.commit()
    connection.close()

remove_old_timetable_entries()

def check_available_appointments():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM timetable')
    available_appointments = bool(cursor.fetchall())
    connection.close()
    return available_appointments

# добавление услуг в базу данных с услугами
def add_info(service, info, time, price):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO info (Service, Info, Time, Price) 
        SELECT ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM info 
            WHERE Service = ? AND Info = ? AND Time = ? AND Price = ?
        )
    """, (service, info, time, price, service, info, time, price))
    connection.commit()
    connection.close()


add_info('Маникюр с покрытием',
         'Входит снятие старого покрытия, опил формы, комби маникюр, выравнивание, покрытие под кутикулу',
         'Продолжительность процедуры - 2 часа', 'Стоимость - 2500 рублей')
add_info('Наращивание',
         'Входит снятие старого покрытия, комби маникюр, создание архитектуры гелем, покрытие гель-лаком под кутикулу',
         'Продолжительность процедуры - 2,5 часа', 'Стоимость - 3500 рублей')
add_info('Маникюр без покрытия', 'Входит снятие старого покрытия, опил формы, комби маникюр',
         'Продолжительность процедуры - 1 час', 'Стоимость - 1000 рублей')
add_info('Снятие покрытия', 'Входит снятие старого покрытия, опил формы', 'Продолжительность процедуры - 15 минут',
         'Стоимость - 500 рублей')
add_info('SPA-уход',
         'Входит очищение кожи с использованием скраба, интенсивное питание кожи маской-филлером, увлажнение кремом с пептидным комплексом',
         '30 минут', 'Стоимость - 700 рублей')
