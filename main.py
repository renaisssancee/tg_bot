import telebot
from telebot import types
bot = telebot.TeleBot('6574248387:AAGILlI3c29I8CqEQYT_xX-cVOTQaj15UM0')

import random
import pandas as pd
import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS timetable
              (Date, Time, Master)''')
#cursor.execute('DELETE FROM timetable;')
cursor.execute('''CREATE TABLE IF NOT EXISTS info
              (Service, Info, Time, Price)''')
#cursor.execute('DELETE FROM info;')
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

add_info('Покрытие', 'однотонное покрытие', '2', '1000')

@bot.message_handler(commands=["start"])
def start(m, res=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Расписание")
    item2 = types.KeyboardButton("Услуги")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(m.chat.id, 'Нажми: \nРасписание для получения окошек, Услуги для информации', reply_markup=markup)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if message.text.strip() == 'Расписание':
        cursor.execute('SELECT * FROM timetable')
        rows = cursor.fetchall()
        rows_str = [' '.join(map(str, row)) for row in rows]
        message_str = '\n'.join(rows_str)
    elif message.text.strip() == 'Услуги':
        cursor.execute('SELECT * FROM info')
        rows = cursor.fetchall()
        rows_str = [', '.join(map(str, row)) for row in rows]
        message_str = '\n'.join(rows_str)
    else:
        message_str = 'нажмите кнопку'
    conn.close()
    bot.send_message(message.chat.id, message_str)

bot.polling(none_stop=True, interval=0)