import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('6574248387:AAGILlI3c29I8CqEQYT_xX-cVOTQaj15UM0')

connection = sqlite3.connect('database.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS timetable
              (Date, Time, Master)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS info
              (Service, Info, Time, Price)''')
connection.commit()
connection.close()

def add_timetable(date, time, master):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO timetable (Date, Time, Master) 
        SELECT ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM timetable 
            WHERE Date = ? AND Time = ? AND Master = ?
        )
    """, (date, time, master, date, time, master))
    connection.commit()
    connection.close()

add_timetable('01.01.2024', '10:00', 'Anna')

def remove_old_timetable_entries(): # это когда нужно очистить базу данных info 
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    # Получаем все записи из базы данных
    cursor.execute('SELECT * FROM info')
    existing_entries = cursor.fetchall()

    # Удаляем записи, которых нет в коде
    for entry in existing_entries:
        cursor.execute('DELETE FROM info WHERE Service = ? AND Info = ? AND Time = ? AND Price = ?', entry)

    connection.commit()
    connection.close()

# Вызываем функцию для удаления старых записей
remove_old_timetable_entries()

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

add_info('\U0001F337 Маникюр с однотонным покрытием гель-лак', 'Входит снятие старого покрытия, опил формы, комби маникюр, выравнивание, покрытие под кутикулу', 'Продолжительность процедуры - 2 часа', 'Стоимость - 2500 рублей')
add_info('\U0001F337 Наращивание', 'Входит снятие старого покрытия, комби маникюр, создание архитектуры гелем, покрытие под кутикулу', 'Продолжительность процедуры - 2,5 часа', 'Стоимость - 3500 рублей')
add_info('\U0001F337 Маникюр без покрытия', 'Входит снятие старого покрытия, опил формы, комби маникюр', 'Продолжительность процедуры - 1 час', 'Стоимость - 1000 рублей')
add_info('\U0001F337 Снятие без маникюра', 'Входитнятие старого покрытия, опил формы', 'Продолжительность процедуры - 15 минут', 'Стоимость - 500 рублей')
add_info('\U0001F337 SPA-уход', 'Входит очищение кожи с использованием скраба, интенсивное питание кожи маской-филлером, увлажнение кремом с пептидным комплексом', '30 минут', 'Стоимость - 700 рублей')

def send_schedule_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Выбрать мастера")
    item2 = types.KeyboardButton("Выбрать время")
    markup.add(item1, item2)
    bot.send_message(chat_id, "Выберите опцию:", reply_markup=markup)

@bot.message_handler(commands=["start"])
def start(m, res=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Расписание")
    item2 = types.KeyboardButton("Услуги")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(m.chat.id, f'Здравствуйте, {m.from_user.first_name}!\nДобро пожаловать в студию smp nails\U0001FA77 \nС помощью этого бота вы сможете: \n \U0001F337 Ознакомиться с услугами салона  \n \U0001F337 Самостоятельно записаться на процедуру \n \U0001F337 Ознакомиться с прайсом \n \U0001F337 Подтвердить или отменить запись')
    bot.send_message(m.chat.id, "Выберите, пожалуйста, что вас интересует\U0001F447", reply_markup=markup)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if message.text.strip() == 'Расписание':
        send_schedule_keyboard(message.chat.id)
        # Дополнительный код, если необходимо что-то еще после выбора "Расписание"

    elif message.text.strip() == 'Услуги':
        cursor.execute('SELECT * FROM info')
        rows = cursor.fetchall()
        rows_str = ['\n'.join(map(str, row)) for row in rows]
        message_str = '\n'.join(rows_str)
        bot.send_message(message.chat.id, message_str)

    elif message.text.strip() == 'Выбрать мастера':
        masters = ['Анна', 'Алина', 'Полина']
        message_str = 'Выберите мастера:\n' + '\n'.join(masters)
        bot.send_message(message.chat.id, message_str)

    elif message.text.strip() == 'Выбрать время':
        time_slots = ['1 января 11.00', '1 января 12.00', '2 января 17.00']
        message_str = 'Выберите время:\n' + '\n'.join(time_slots)
        bot.send_message(message.chat.id, message_str)

    else:
        bot.send_message(message.chat.id, 'нажмите кнопку')

    conn.close()


bot.polling(none_stop=True, interval=0)

