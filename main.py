import telebot
from telebot import types
from telebot.types import Message
import sqlite3
from create_db import create_tables
from operations_database import get_available_times, add_timetable, remove_old_timetable_entries, \
    check_available_appointments, add_info

bot = telebot.TeleBot('6574248387:AAGILlI3c29I8CqEQYT_xX-cVOTQaj15UM0')

user_sessions = {}
available_appointments = True
create_tables()

# кнопочки
def send_schedule_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Выбрать мастера")
    item2 = types.KeyboardButton("Выбрать время")
    item3 = types.KeyboardButton("Назад")
    markup.add(item1, item2, item3)
    bot.send_message(chat_id, "Выберите опцию:", reply_markup=markup)

# кнопочки с услугами
def send_inline_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup()
    services = ['Маникюр с покрытием', 'Наращивание', 'Маникюр без покрытия', 'Снятие покрытия', 'SPA-уход']
    for service in services:
        button = types.InlineKeyboardButton(text=service, callback_data=f"choose_option_{service}")
        markup.add(button)
    bot.send_message(chat_id, "Выберите услугу:", reply_markup=markup)


def send_only_back_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Назад")
    markup.add(item1)
    bot.send_message(chat_id, "Редактируйте слоты или нажмите кнопку для выхода", reply_markup=markup)

def get_master_request(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(text='Добавить слот')
    item2 = types.KeyboardButton(text='Удалить слот')
    markup.add(item1)
    markup.add(item2)

    msg = bot.send_message(message.chat.id, "Выбери действие", reply_markup=markup)
    bot.register_next_step_handler(msg, check_master_request)

def check_master_request(message):
    request = message.text
    if request == 'Добавить слот':
        add_slot(message)
    elif request == 'Удалить слот':
        remove_slot(message)
    else:
        bot.send_message(message.chat.id, "Неверный ввод")
        return

# возможность для мастера добавить окошко
def add_slot(message):
    chat_id = message.chat.id
    send_only_back_keyboard(chat_id)
    data = {'date': None, 'time': None, 'master': None}

    def ask_for_date():
        msg = bot.send_message(chat_id, 'Введите дату в формате DD.MM.YYYY')
        bot.register_next_step_handler(msg, process_date)

    def process_date(message):
        data['date'] = message.text
        if data['date'] == 'Назад':
            start(message)
            return
        ask_for_time()

    def ask_for_time():
        msg = bot.send_message(chat_id, 'Введите время в формате HH:MM')
        bot.register_next_step_handler(msg, process_time)

    def process_time(message):
        data['time'] = message.text
        if data['time'] == 'Назад':
            start(message)
            return
        ask_for_master()

    def ask_for_master():
        msg = bot.send_message(chat_id, 'Введите Имя:')
        bot.register_next_step_handler(msg, process_master)

    def process_master(message):
        data['master'] = message.text
        if data['master'] == 'Назад':
            start(message)
            return
        finish()

    def finish():
        bot.send_message(chat_id, 'Ваш слот добавлен, вернитесь в главное меню по кнопке')
        add_timetable(data['date'] + ' ' + data['time'], data['master'])

    ask_for_date()

def remove_slot(message):
    chat_id = message.chat.id
    send_only_back_keyboard(chat_id)
    data = {'name': None, 'slot': None}

    def ask_for_name():
        msg = bot.send_message(chat_id, 'Введите имя')
        bot.register_next_step_handler(msg, process_name)

    def process_name(message):
        data['name'] = message.text.strip()
        if data['name'] == 'Назад':
            start(message)
            return

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT DateTime FROM timetable WHERE Master = ?", (data['name'],))
        services = cursor.fetchall()
        connection.close()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for service in services:
            service_name = service[0]
            item1 = types.KeyboardButton(text=service_name)
            markup.add(item1)

        msg = bot.send_message(message.chat.id, "Выберите слот", reply_markup=markup)
        bot.register_next_step_handler(msg, process_slot)

    def process_slot(message):
        data['slot'] = message.text
        if data['slot'] == 'Назад':
            start(message)
            return
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM timetable WHERE Master = ? AND DateTime = ?", (data['name'], data['slot']))
        connection.commit()
        connection.close()

        send_only_back_keyboard(chat_id)
        bot.send_message(chat_id, 'Ваш слот удален, вернитесь в главное меню по кнопке')

    ask_for_name()


# ввод пароля
def get_password(message):
    markup = types.InlineKeyboardMarkup()
    msg = bot.send_message(message.chat.id, 'Введите пароль: ', reply_markup=markup)
    bot.register_next_step_handler(msg, check_password)

# проверка пароля для доступа к редактированию записей мастера
def check_password(message):
    password = 1234
    try:
        user_input = int(message.text)
        if user_input == password:
            bot.send_message(message.chat.id, 'Доступ разрешен')
            get_master_request(message)
        elif user_input == 0:
            start(message)
        else:
            bot.send_message(message.chat.id, 'Неверный пароль, перезайдите')
    except ValueError:
        bot.send_message(message.chat.id, 'Пароль состоит из цифр, перезайдите')

# стартовая команда
@bot.message_handler(commands=['start'])
def start(message):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()

    # Проверка наличия доступных записей
    global available_appointments
    available_appointments = check_available_appointments()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Запись в салон")
    item2 = types.KeyboardButton("Услуги")
    item3 = types.KeyboardButton("Мои записи")
    item4 = types.KeyboardButton("Я мастер")
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    markup.add(item4)

    if not available_appointments:
        bot.send_message(message.chat.id, "К сожалению, на данный момент нет доступных записей.")
    else:
        bot.send_message(message.chat.id,
                         f'Здравствуйте, {message.from_user.first_name}!\nДобро пожаловать в студию smp nails\U0001FA77 \nС помощью этого бота вы сможете: \n \U0001F337 Ознакомиться с услугами салона  \n \U0001F337 Самостоятельно записаться на процедуру \n \U0001F337 Ознакомиться с прайсом \n \U0001F337 Подтвердить или отменить запись')
        bot.send_message(message.chat.id, "Выберите, пожалуйста, что вас интересует\U0001F447", reply_markup=markup)

    connect.close()


# вывод информации по выбранной кнопке
@bot.message_handler(content_types=["text"])
def handle_text(message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if message.text.strip() == 'Запись в салон':
        send_schedule_keyboard(message.chat.id)

    elif message.text.strip() == 'Услуги':
        send_inline_keyboard(message.chat.id)

    elif message.text.strip() == 'Мои записи':
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        user_id = message.chat.id
        cursor.execute(f'SELECT id, time_slot, procedure, master_name, status FROM appointments WHERE id = {user_id}')
        appointments = cursor.fetchall()

        if len(appointments) == 0:
            bot.send_message(message.chat.id, "У вас нет предстоящих записей")
        else:
            bot.send_message(message.chat.id, "Ваши предстоящие записи:")
            for i, appointment in enumerate(appointments):
                appointment_id, time_slot, procedure, master_name, status = appointment[0], appointment[1], appointment[2], appointment[3], appointment[4]
                
                if status == 'pending':
                    inline_buttons = [
                        types.InlineKeyboardButton(
                            text=f"Отменить: {time_slot}, {procedure}",
                            callback_data=f"delete_appointment_{i + 1}"
                        ),
                        types.InlineKeyboardButton(
                            text="Подтвердить",
                            callback_data=f"confirm_appointment_{i + 1}"
                        )
                    ]
                else:
                    inline_buttons = []  

                markup = types.InlineKeyboardMarkup().add(*inline_buttons)
                bot.send_message(message.chat.id, f"Дата и время: {time_slot}, Услуга: {procedure}, Мастер: {master_name}", reply_markup=markup)
        connection.close()

    elif message.text.strip() == 'Я мастер':
        if get_password(message) == 1:
            get_master_request(message)

    elif message.text.strip() == 'Выбрать мастера':
        markup = types.InlineKeyboardMarkup()
        cursor.execute('SELECT DISTINCT Master FROM timetable')
        masters = [row[0] for row in cursor.fetchall()]
        for master in masters:
            button = types.InlineKeyboardButton(text=master, callback_data=f"choose_master_{master}")
            markup.add(button)
        bot.send_message(message.chat.id, "Выберите мастера:", reply_markup=markup)


    elif message.text.strip() == 'Выбрать время':
        markup = types.InlineKeyboardMarkup()
        cursor.execute('SELECT DISTINCT Master FROM timetable')
        masters = [row[0] for row in cursor.fetchall()]
        for master in masters:
            available_times = get_available_times(master)
            for time_slot in available_times:
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

def send_appointment_deleted_message(chat_id):
    bot.send_message(chat_id, "Запись отменена")

def send_appointment_confirmed_message(chat_id):
    bot.send_message(chat_id, "Запись подтверждена")

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_appointment_'))
def delete_appointment_callback(call):
    appointment_index = int(call.data.split('_')[-1]) - 1
    user_id = call.message.chat.id

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute(f'SELECT time_slot, procedure, master_name FROM appointments WHERE id = {user_id}')
    appointments = cursor.fetchall()

    if 0 <= appointment_index < len(appointments):
        time_slot, procedure, master_name = appointments[appointment_index]
        cursor.execute("DELETE FROM appointments WHERE id = ? AND time_slot = ? AND procedure = ? AND master_name = ?", (user_id, time_slot, procedure, master_name))
        cursor.execute("""
        INSERT INTO timetable (DateTime, Master) 
        SELECT ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM timetable 
            WHERE DateTime = ? AND Master = ?
        )
    """, (time_slot, master_name, time_slot, master_name))
        connection.commit()
        connection.close()

        send_appointment_deleted_message(user_id)
    else:
        connection.close()
        bot.send_message(call.id, text="Ошибка при отмене записи")

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_appointment_'))
def confirm_appointment_callback(call):
    appointment_index = int(call.data.split('_')[-1]) - 1
    user_id = call.message.chat.id

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute(f'SELECT id, time_slot, procedure, master_name, status FROM appointments WHERE id = {user_id}')
    appointments = cursor.fetchall()

    if 0 <= appointment_index < len(appointments):
        appointment_id, time_slot, procedure, master_name, status = appointments[appointment_index]
        if status == 'pending':
            cursor.execute("UPDATE appointments SET status = 'confirmed' WHERE id = ? AND time_slot = ? AND procedure = ? AND master_name = ?", (user_id, time_slot, procedure, master_name))
            connection.commit()
            connection.close()

            send_appointment_confirmed_message(call.message.chat.id)
        else:
            connection.close()
            bot.send_message(call.message.chat.id, "Эта запись уже подтверждена.")
    else:
        connection.close()
        bot.send_message(call.message.chat.id, "Ошибка при подтверждении записи")


@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_master_'))
def callback_choose_master(call):
    master_name = call.data.split('_')[-1]
    available_times = get_available_times(master_name)

    if available_times:
        markup = types.InlineKeyboardMarkup()
        for time in available_times:
            button = types.InlineKeyboardButton(text=time, callback_data=f"choose_time_{master_name}_{time}")
            markup.add(button)
        bot.send_message(call.message.chat.id, f"Выберите свободное время для мастера {master_name}:",
                         reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id,
                         f"На выбранную дату все слоты мастра {master_name} заняты. Выберите другого мастера или дату.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_option_'))
def callback_show_service(call):
    service_name = call.data.split('_')[-1].replace('_', ' ')
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


@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_time_'))
def callback_enter_name(call):
    bot.send_message(call.message.chat.id, "Для записи в салон введите свое имя")

    bot.register_next_step_handler(call.message, process_enter_phone, call.data)

def process_enter_phone(message, data):
    master_name, time_slot = data.split('_')[2], data.split('_')[-1]

    customer_name = message.text
    if customer_name == 'Назад':
        start(message)
        return

    bot.send_message(message.chat.id, "Введите номер телефона")

    bot.register_next_step_handler(message, lambda message: process_enter_procedure(message, master_name, time_slot, customer_name))

def process_enter_procedure(message, master_name, time_slot, customer_name):
    customer_phone = message.text
    if customer_phone == 'Назад':
        start(message)
        return

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute("SELECT Service FROM info")
    services = cursor.fetchall()
    connection.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for service in services:
        service_name = service[0]
        item1 = types.KeyboardButton(text=service_name)
        markup.add(item1)

    bot.send_message(message.chat.id, "Выберите название процедуры", reply_markup=markup)

    bot.register_next_step_handler(message, lambda message: process_generate_appointment(message, master_name, time_slot, customer_name, customer_phone))

def process_generate_appointment(message, master_name, time_slot, customer_name, customer_phone):
    procedure = message.text
    if procedure == 'Назад':
        start(message)
        return

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    available_times = get_available_times(master_name)
    if time_slot not in available_times:
        connection.close()
        bot.send_message(message.chat.id, f"Извините, время {time_slot} уже занято. Выберите другое время.")
        return

    if time_slot not in [str(time) for time in available_times]:
        connection.close()
        bot.send_message(message.chat.id, "Выбранное время недопустимо. Пожалуйста, выберите доступное время.")
        return

    user_id = message.chat.id
    values = [user_id, master_name, time_slot, customer_name, customer_phone, procedure]
    cursor.execute("INSERT INTO appointments VALUES(?, ?, ?, ?, ?, ?, 'pending');", values)

    cursor.execute("DELETE FROM timetable WHERE Master = ? AND DateTime = ?", (master_name, time_slot))

    connection.commit()
    connection.close()

    success_message = f"Вы успешно записаны на {procedure} на {time_slot} к мастеру {master_name}"

    return_to_main_markup = types.InlineKeyboardMarkup()
    return_button = types.InlineKeyboardButton(text="Вернуться на главный экран", callback_data="return_to_main")
    return_to_main_markup.add(return_button)

    bot.send_message(message.chat.id, success_message, reply_markup=return_to_main_markup)


@bot.callback_query_handler(func=lambda call: call.data == "return_to_main")
def return_to_main_screen_callback(call):
    start(call.message)

bot.polling(none_stop=True, interval=0)