import telebot
import psycopg2
import os
from protect import do_some_protection
from const import token
import time
from telebot import types
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

do_some_protection()
bot = telebot.TeleBot(token)


def city(update,context):
  list_of_cities = ['Erode','Coimbatore','London', 'Thunder Bay', 'California']
  button_list = []
  for each in list_of_cities:
     button_list.append(InlineKeyboardButton(each, callback_data = each))
  reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=1)) #n_cols = 1 is for single column and mutliple rows
  bot.send_message(chat_id=update.message.chat_id, text='Choose from the following',reply_markup=reply_markup)


def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
  menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
  if header_buttons:
    menu.insert(0, header_buttons)
  if footer_buttons:
    menu.append(footer_buttons)
  return menul



@bot.message_handler(commands=['start'])
def send_welcome(message):
   
    bot.reply_to(message, "Привет я бот для фотохостинга.")
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('загруженные мной ')
    itembtn2 = types.KeyboardButton('сменить пароль')
    itembtn3 = types.KeyboardButton('инструкции по эксплуатации')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Выбирите опции:", reply_markup=markup)

    #bot.send_message(message['chat']['id'], "Choose one letter:", reply_markup=markup)


@bot.message_handler(commands=['help'])
def help_command(message):
   keyboard = telebot.types.InlineKeyboardMarkup()
   keyboard.add(
       telebot.types.InlineKeyboardButton(
           'Message the developer', url='telegram.me/none'
       )
   )
   bot.send_message(
       message.chat.id,
       '1) To receive a list of available currencies press /exchange.\n' +
       '2) Click on the currency you are interested in.\n' +
       '3) You will receive a message containing information regarding the source and the target currencies, ' +
       'buying rates and selling rates.\n' +
       '4) Click “Update” to receive the current information regarding the request. ' +
       'The bot will also show the difference between the previous and the current exchange rates.\n' +
       '5) The bot supports inline. Type @<botusername> in any chat and the first letters of a currency.',
       reply_markup=keyboard
   )






@bot.message_handler(regexp="загруженные мной")
def my_uploads(message):
    bot.send_message(message.chat.id, "instar:")
    
@bot.message_handler(regexp="инструкции по эксплуатации")
def instructions(message):
    bot.send_message(message.chat.id, "upoaded:")


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
