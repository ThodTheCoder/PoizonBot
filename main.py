from currency_converter import CurrencyConverter
from flask import Flask, request
from telebot import types
import sqlite3 as sql
import logging
import telebot
import random
import os


bot = telebot.TeleBot('6962140661:AAGH5Lf1Ig9-qQ44FOVL4FH1epHJ5nfDR6A')
currency = CurrencyConverter()
admin = 742773729


@bot.message_handler(commands=['start', 'restart'])
def start(message):
    global admin

    try:
        if message.from_user.id != admin:
            con = sql.connect('main.db')
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                        "userID TEXT, username TEXT)")
            cur.execute('SELECT * FROM users WHERE userID = ?', (message.from_user.id,))
            userRec = cur.fetchone()
            if userRec:
                pass
            else:
                cur.execute("INSERT INTO users (userID, username) VALUES ('%s', '%s')" % (message.from_user.id, message.from_user.username))
                con.commit()
            cur.close()
            con.close()

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bt1 = types.KeyboardButton('Посчитать цену')
            bt2 = types.KeyboardButton('Сделать заказ')
            bt3 = types.KeyboardButton('Отследить товар')
            markup.row(bt1, bt2)
            markup.row(bt3)

            bot.send_message(message.chat.id, f'<b>Приветствую, @{message.from_user.username}!</b>', reply_markup=markup, parse_mode='html')
            bot.send_message(message.chat.id, f'Этот бот поможет тебе посчитать стоимость товаров, а также тут можно делать и отслеживать заказы.', parse_mode='html')
        else:
            con = sql.connect('main.db')
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                        "username TEXT, orderID TEXT, description TEXT, status TEXT)")
            cur.close()
            con.close()

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bt1 = types.KeyboardButton('Внести заказ в базу данных')
            bt2 = types.KeyboardButton('Поменять статус заказа')
            markup.row(bt1)
            markup.row(bt2)
            bot.send_message(message.chat.id, f'<b>Приветствую, Администратор!</b>',
                             reply_markup=markup, parse_mode='html')
    except Exception as e:
        bot.send_message(message.chat.id, "<b>Произошла ошибка.</b>", parse_mode='html')
        print("Ошибка:", str(e))


@bot.message_handler()
def info(message):
    global admin

    if message.text == 'Посчитать цену':
        bot.send_message(message.chat.id, "Введите сумму в <b><u>CNY (Китайский юань):</u></b>", parse_mode='html')
        bot.register_next_step_handler(message, Convert)

    elif message.text == 'Сделать заказ':
        bot.send_message(message.chat.id, "Введите название товара на <b><u>POIZON:</u></b>", parse_mode='html')
        bot.register_next_step_handler(message, Order)

    elif message.text == 'Отследить товар':
        bot.send_message(message.chat.id, "<b>Введи <u>id</u> заказа:</b>",
                         parse_mode='html')
        bot.register_next_step_handler(message, CheckOrder)

    elif message.text == 'Внести заказ в базу данных':
        if message.from_user.id == admin:
            bot.send_message(message.chat.id, "<b>Введи <u>@никнейм</u> пользователя и <u>id</u> заказа через пробел:</b>", parse_mode='html')
            bot.register_next_step_handler(message, NewOrder)
        else:
            pass

    elif message.text == 'Поменять статус заказа':
        if message.from_user.id == admin:
            bot.send_message(message.chat.id, "<b>Введи <u>id</u> заказа, который хочешь обновить:</b>",
                             parse_mode='html')
            bot.register_next_step_handler(message, ReOrder)
        else:
            pass


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global admin

    if 'sendToAdmin' in callback.data:
        bot.send_message(admin, f"Пользователь <b>@{callback.from_user.username}</b> хочет приобрести <b>{callback.data.split('/')[1]}!</b>", parse_mode='html')
        bot.send_message(callback.from_user.id, f"Администратор скоро с вами свяжется!")

    elif callback.data == 'newOrder':
        bot.send_message(callback.message.chat.id, "Введите название товара на <b><u>POIZON:</u></b>", parse_mode='html')
        bot.register_next_step_handler(callback.message, Order)

    elif 'status/' in callback.data:
        n = int(callback.data.split('/')[1])
        orderID = callback.data.split('/')[2]

        con = sql.connect('main.db')
        cur = con.cursor()
        if n == 1:
            cur.execute("UPDATE orders SET status = ? WHERE orderID = ?", ('Заказ создан', orderID,))
            con.commit()
        elif n == 2:
            cur.execute("UPDATE orders SET status = ? WHERE orderID = ?", ('Товар выкуплен', orderID,))
            con.commit()
        elif n == 3:
            cur.execute("UPDATE orders SET status = ? WHERE orderID = ?", ('Товар в пути на склад в Гуанчжоу', orderID,))
            con.commit()
        elif n == 4:
            cur.execute("UPDATE orders SET status = ? WHERE orderID = ?", ('Товар на складе в Гуанчжоу', orderID,))
            con.commit()
        elif n == 5:
            cur.execute("UPDATE orders SET status = ? WHERE orderID = ?", ('Товар отправлен из Гуанчжоу в Россию', orderID,))
            con.commit()
        elif n == 6:
            cur.execute("UPDATE orders SET status = ? WHERE orderID = ?", ('Товар готов к получению', orderID,))
            con.commit()
        cur.close()
        con.close()

        bot.send_message(callback.message.chat.id, "<b>Заказ добавлен!</b>", parse_mode='html')

    elif 'newStatus/' in callback.data:
        n = int(callback.data.split('/')[1])
        orderID = callback.data.split('/')[2]

        con = sql.connect('main.db')
        cur = con.cursor()
        if n == 1:
            cur.execute("UPDATE orders SET status = ? WHERE orderID = ?", ('Заказ создан', orderID,))
            con.commit()
        elif n == 2:
            cur.execute("UPDATE orders SET status = ? WHERE orderID = ?", ('Товар выкуплен', orderID,))
            con.commit()
        elif n == 3:
            cur.execute("UPDATE orders SET status = ? WHERE orderID = ?",
                        ('Товар в пути на склад в Гуанчжоу', orderID,))
            con.commit()
        elif n == 4:
            cur.execute("UPDATE orders SET status = ? WHERE orderID = ?", ('Товар на складе в Гуанчжоу', orderID,))
            con.commit()
        elif n == 5:
            cur.execute("UPDATE orders SET status = ? WHERE orderID = ?",
                        ('Товар отправлен из Гуанчжоу в Россию', orderID,))
            con.commit()
        elif n == 6:
            cur.execute("UPDATE orders SET status = ? WHERE orderID = ?", ('Товар готов к получению', orderID,))
            con.commit()
        cur.close()
        con.close()

        bot.send_message(callback.message.chat.id, "<b>Заказ обновлён!</b>", parse_mode='html')


def Convert(message):
    try:
        price = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "<b>Неверный формат! Введите сумму:</b>", parse_mode='html')
        bot.register_next_step_handler(message, Convert)
        return

    if price > 0:
        second = currency.convert(price, 'RUB', 'CNY')
        rub = (price / second) * price
        bot.send_message(message.chat.id, f"По текущему курсу:\n\n<b>{price}</b> CNY = <b>{round(rub, 2)}</b> RUB", parse_mode='html')
    else:
        bot.send_message(message.chat.id, "<b>Неверное значение! Введите сумму:</b>", parse_mode='html')
        bot.register_next_step_handler(message, Convert)


def Order(message):
    markup = types.InlineKeyboardMarkup()
    bt1 = types.InlineKeyboardButton('Да!', callback_data='sendToAdmin/'+message.text)
    bt2 = types.InlineKeyboardButton('Заново', callback_data='newOrder')
    markup.row(bt1, bt2)
    bot.send_message(message.chat.id, f"Вы хотите приобрести:\n\n• <b>{message.text}</b>", reply_markup=markup, parse_mode='html')


def NewOrder(message):
    username = message.text.split(' ')[0][1:]
    orderID = message.text.split(' ')[1]

    con = sql.connect('main.db')
    cur = con.cursor()
    cur.execute("INSERT INTO orders (username, orderID, description, status) VALUES ('%s', '%s', '%s', '%s')" % (username, orderID, '0', '0'))
    cur.execute("UPDATE orders SET orderID = ? WHERE username = ?", (orderID, username,))
    con.commit()
    cur.close()
    con.close()

    bot.send_message(message.chat.id, "<b>Введи <u>название</u> товара:</b>", parse_mode='html')
    bot.register_next_step_handler(message, Product, orderID)


def Product(message, orderID):
    con = sql.connect('main.db')
    cur = con.cursor()
    cur.execute("UPDATE orders SET description = ? WHERE orderID = ?", (message.text, orderID,))
    con.commit()
    cur.close()
    con.close()

    markup = types.InlineKeyboardMarkup()
    bt1 = types.InlineKeyboardButton('Заказ создан', callback_data='status/1/'+str(orderID))
    bt2 = types.InlineKeyboardButton('Товар выкуплен', callback_data='status/2/'+str(orderID))
    bt3 = types.InlineKeyboardButton('На пути в склад', callback_data='status/3/'+str(orderID))
    bt4 = types.InlineKeyboardButton('Товар в Гуанчжоу', callback_data='status/4/'+str(orderID))
    bt5 = types.InlineKeyboardButton('Отправлен в РФ', callback_data='status/5/'+str(orderID))
    bt6 = types.InlineKeyboardButton('Готов к получению', callback_data='status/6/'+str(orderID))
    markup.row(bt1, bt2)
    markup.row(bt3, bt4)
    markup.row(bt5, bt6)

    bot.send_message(message.chat.id, "<b>Выбери <u>статус</u> товара:</b>", reply_markup=markup, parse_mode='html')


def ReOrder(message):
    con = sql.connect('main.db')
    cur = con.cursor()
    description = cur.execute("SELECT description FROM orders WHERE orderID = ?", (message.text,))
    description = cur.fetchone()
    status = cur.execute("SELECT status FROM orders WHERE orderID = ?", (message.text,))
    status = cur.fetchone()
    cur.close()
    con.close()

    markup = types.InlineKeyboardMarkup()
    bt1 = types.InlineKeyboardButton('Заказ создан', callback_data='newStatus/1/' + str(message.text))
    bt2 = types.InlineKeyboardButton('Товар выкуплен', callback_data='newStatus/2/' + str(message.text))
    bt3 = types.InlineKeyboardButton('В пути на склад', callback_data='newStatus/3/' + str(message.text))
    bt4 = types.InlineKeyboardButton('Товар в Гуанчжоу', callback_data='newStatus/4/' + str(message.text))
    bt5 = types.InlineKeyboardButton('Отправлен в РФ', callback_data='newStatus/5/' + str(message.text))
    bt6 = types.InlineKeyboardButton('Готов к получению', callback_data='newStatus/6/' + str(message.text))
    markup.row(bt1, bt2)
    markup.row(bt3, bt4)
    markup.row(bt5, bt6)

    bot.send_message(message.chat.id, f"<b>Товар:</b> <u>{description[0]}</u>\n<b>Статус:</b> <u>{status[0]}</u>\n\nВыбери новый статус:", reply_markup=markup, parse_mode='html')


def CheckOrder(message):
    con = sql.connect('main.db')
    cur = con.cursor()
    username = cur.execute("SELECT username FROM orders WHERE orderID = ?", (message.text,))
    username = cur.fetchone()
    description = cur.execute("SELECT description FROM orders WHERE orderID = ?", (message.text,))
    description = cur.fetchone()
    status = cur.execute("SELECT status FROM orders WHERE orderID = ?", (message.text,))
    status = cur.fetchone()
    cur.close()
    con.close()

    if username[0] == message.from_user.username:
        bot.send_message(message.chat.id, f"<b>ID заказа:</b> <u>{message.text}</u>\n<b>Товар:</b> <u>{description[0]}</u>\n<b>Статус:</b> <u>{status[0]}</u>", parse_mode='html')
    else:
        bot.send_message(message.chat.id, f"<b>У вас нет заказов с таким <u>id</u>!</b>", parse_mode='html')


if "HEROKU" in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    server = Flask(__name__)
    @server.route("/bot", methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200
    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url="https://min-gallows.herokuapp.com/bot") # этот url нужно заменить на url вашего Хероку приложения
        return "?", 200
    server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
else:
    bot.remove_webhook()
    bot.polling(none_stop=True)