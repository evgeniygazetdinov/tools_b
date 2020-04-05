import telebot
import psycopg2
import os
from protect import do_some_protection
from const import token
import time
from telebot import types


#do_some_protection()
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Напиши мне номер модели, и ты получишь всю необходимую информацию\n" +
                 "Если же ты хочешь добавить свою технику в нашу базу для быстрого поиска клиентов, то сделать это можно по ссылке: " +
                 "www.sklad-kamaz.ru")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(message)
    



""""
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    conn = psycopg2.connect(dbname=os.environ['dbname'], user=os.environ['user'],
                            password=os.environ['password'],
                            host=os.environ['host'])

    cursor = conn.cursor()
    cursor.execute(
        'SELECT home_dealer.name, home_dealer.phone_number, home_car.model, home_car.year, home_car.city, home_car.count FROM home_car, home_dealer WHERE home_car.user_id = home_dealer.id AND model = %s',
        (message.text,))
    s = True
    for row in cursor:
        bot.reply_to(message, ('Компания: ' + str(row[0]) + '\nНомер телефона: ' + str(row[1]) + '\nМодель: ' + str(
            row[2]) + '\nГод: ' + str(row[3]) + '\nГород: ' + str(row[4]) + '\nКоличество: ' + str(row[5])))
        s = False
    if s:
        bot.reply_to(message, 'К сожалению, данной модели нет в наличии')
    cursor.close()
    conn.close()
"""

bot.polling(none_stop=True, timeout=123)
