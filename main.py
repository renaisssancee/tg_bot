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

# Добавление информации о времени работы мастеров
masters_schedule = {
    'Анна': ['11:00', '12:00'],
    'Алина': ['13:00', '14:00'],
    'Полина': ['15:00', '16:00'],
}

# Функция для получения свободного времени мастера
def get_available_times(master):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT Time FROM timetable WHERE Master = ? AND Date = ?', (master, '01.01.2024'))
    scheduled_times = [row[0] for row in cursor.fetchall()]
    connection.close()
    return [time for time in masters_schedule[master] if time not in scheduled_times]

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

def remove_old_timetable_entries():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM info')
    connection.commit()
    connection.close()

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

add_info('Маникюр с покрытием', 'Входит снятие старого покрытия, опил формы, комби маникюр, выравнивание, покрытие под кутикулу', 'Продолжительность процедуры - 2 часа', 'Стоимость - 2500 рублей')
add_info('Наращивание', 'Входит снятие старого покрытия, комби маникюр, создание архитектуры гелем, покрытие гель-лаком под кутикулу', 'Продолжительность процедуры - 2,5 часа', 'Стоимость - 3500 рублей')
add_info('Маникюр без покрытия', 'Входит снятие старого покрытия, опил формы, комби маникюр', 'Продолжительность процедуры - 1 час', 'Стоимость - 1000 рублей')
add_info('Снятие покрытия', 'Входит снятие старого покрытия, опил формы', 'Продолжительность процедуры - 15 минут', 'Стоимость - 500 рублей')
add_info('SPA-уход', 'Входит очищение кожи с использованием скраба, интенсивное питание кожи маской-филлером, увлажнение кремом с пептидным комплексом', '30 минут', 'Стоимость - 700 рублей')

def send_schedule_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Выбрать мастера")
    item2 = types.KeyboardButton("Выбрать время")
    item3 = types.KeyboardButton("Назад")
    markup.add(item1, item2, item3)
    bot.send_message(chat_id, "Выберите опцию:", reply_markup=markup)

def send_inline_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup()
    services = ['Маникюр с покрытием', 'Наращивание', 'Маникюр без покрытия', 'Снятие покрытия', 'SPA-уход']
    for service in services:
        button = types.InlineKeyboardButton(text=service, callback_data=f"choose_option_{service}")
        markup.add(button)
    bot.send_message(chat_id, "Выберите услугу:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(id INTEGER)""")
    connect.commit()

    people_id = message.chat.id
    cursor.execute(f"SELECT id FROM login_id WHERE id = {people_id}")
    data = cursor.fetchone()

    if data is None:
        user_id = [message.chat.id]
        cursor.execute("INSERT INTO login_id VALUES(?);", user_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Расписание")
    item2 = types.KeyboardButton("Услуги")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}!\nДобро пожаловать в студию smp nails\U0001FA77 \nС помощью этого бота вы сможете: \n \U0001F337 Ознакомиться с услугами салона  \n \U0001F337 Самостоятельно записаться на процедуру \n \U0001F337 Ознакомиться с прайсом \n \U0001F337 Подтвердить или отменить запись')
    bot.send_message(message.chat.id, "Выберите, пожалуйста, что вас интересует\U0001F447", reply_markup=markup)

    connect.close()

# @bot.message_handler(commands=["start"])
# def start(m, res=False):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     item1 = types.KeyboardButton("Расписание")
#     item2 = types.KeyboardButton("Услуги")
#     markup.add(item1)
#     markup.add(item2)
#     bot.send_message(m.chat.id, f'Здравствуйте, {m.from_user.first_name}!\nДобро пожаловать в студию smp nails\U0001FA77 \nС помощью этого бота вы сможете: \n \U0001F337 Ознакомиться с услугами салона  \n \U0001F337 Самостоятельно записаться на процедуру \n \U0001F337 Ознакомиться с прайсом \n \U0001F337 Подтвердить или отменить запись')
#     bot.send_message(m.chat.id, "Выберите, пожалуйста, что вас интересует\U0001F447", reply_markup=markup)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if message.text.strip() == 'Расписание':
        send_schedule_keyboard(message.chat.id)

    elif message.text.strip() == 'Услуги':
        send_inline_keyboard(message.chat.id)

    elif message.text.strip() == 'Выбрать мастера':
        markup = types.InlineKeyboardMarkup()
        for master in masters_schedule.keys():
            button = types.InlineKeyboardButton(text=master, callback_data=f"choose_master_{master}")
            markup.add(button)
        bot.send_message(message.chat.id, "Выберите мастера:", reply_markup=markup)


    elif message.text.strip() == 'Выбрать время':
        markup = types.InlineKeyboardMarkup()
        for master, working_hours in masters_schedule.items():
            for time_slot in working_hours:
                button_text = f"{master}: {time_slot}"
                callback_data = f"choose_time_{master}_{time_slot}"
                button = types.InlineKeyboardButton(text=button_text, callback_data=callback_data)
                markup.add(button)
        bot.send_message(message.chat.id, "Выберите время:", reply_markup=markup)


    elif message.text.strip() == 'Назад':
        start(message)
    
    else:
        bot.send_message(message.chat.id, 'нажмите кнопку')

    conn.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_option_'))
def callback_show_service(call):
    service_name = call.data.split('_')[-1].replace('_', ' ')  # Replace underscores with spaces
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM info WHERE Service = ?', (service_name,))
    service_info = cursor.fetchone()
    connection.close()

    if service_info:
        info_message = f"{service_info[0]}\n{service_info[1]}\n{service_info[2]}\n{service_info[3]}"
        bot.send_message(call.message.chat.id, info_message)
    else:
        bot.send_message(call.message.chat.id, "Информация не найдена.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_master_'))
def callback_choose_master(call):
    master_name = call.data.split('_')[-1]
    available_times = get_available_times(master_name)

    if available_times:
        markup = types.InlineKeyboardMarkup()
        for time in available_times:
            button = types.InlineKeyboardButton(text=time, callback_data=f"choose_time_{master_name}_{time}")
            markup.add(button)
        bot.send_message(call.message.chat.id, f"Выберите свободное время для мастера {master_name}:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, f"На выбранную дату все слоты мастра {master_name} заняты. Выберите другого мастера или дату.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_time_'))
def callback_choose_time(call):
    master_name, time_slot = call.data.split('_')[2], call.data.split('_')[-1]
    bot.send_message(call.message.chat.id, f"Вы успешно записаны на {time_slot} к мастеру {master_name}")

bot.polling(none_stop=True, interval=0)
