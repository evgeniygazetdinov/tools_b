import json
import requests
import time
import urllib
from const import token as TOKEN
from dbhelper import DBHelper
from protect import do_some_protection

URL = "https://api.telegram.org/bot{}/".format(TOKEN)


db = DBHelper()
menu_items = ['login','help']
login_items = ['my_uploads','change_password', 'instructions','end_sessions']
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def build_keyboard(items):
    keyboard = [[item]for item in items]
    reply_markup = {'keyboard':keyboard, 'one_time_keyboard':True}
    return json.dumps(reply_markup)


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)




def login_handler(updates):
    for update in updates["result"]:
        chat = update["message"]["chat"]["id"]
        
        try:
            text = update["message"]["text"]
            
            items = db.get_items(chat)
            if text =='/start':
                #check_user_exist()
                #if not exist create_user
                #exist this menu
                keyboard = build_keyboard(menu_items)
                send_message('Choose your variant', chat, keyboard)
            if text == 'login':

               keyboard = build_keyboard(login_items)
               send_message('Choose your variant', chat, keyboard)
           
        except Exception  as e:
            print(e)
            send_message('this not look a text',chat)

def sucess_login_hanler(updates):
    for update in updates["result"]:
        chat = update["message"]["chat"]["id"]
        
        try:
            text = update["message"]["text"]
            
            items = db.get_items(chat)
            if text =='/start':
                #check_user_exist()
                #if not exist create_user
                #exist this menu
                keyboard = build_keyboard(menu_items)
                send_message('Choose your variant', chat, keyboard)
            if text == 'login':

               keyboard = build_keyboard(login_items)
               send_message('Choose your variant', chat, keyboard)
           
        except Exception  as e:
            print(e)
            send_message('this not look a text',chat)




def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) != 0:
            last_update_id = get_last_update_id(updates) + 1
            #check here picture or message
            cur_user = updates['result'][0]['message']['chat']['username']
            cur_chat = updates['result'][0]["message"]["chat"]["id"]
            cur_message = updates['result'][0]['message']['chat']['username']
            #if cur_user:#user_exist(cur_user):
            #    pass
                #login_handler()
                #if login_handler:
                #    message_handler()
            #else:
                #message you dont registred
                #password_handler()
            send_message('hello {} you not registed. please type your password look like "my_password=YOUR PASSWORD"'.format(cur_user), cur_chat) 
            
            print('here')
                #create_new_user_handler(cur_user)
        time.sleep(0.5)


if __name__ == '__main__':
    db.setup()
    do_some_protection()
    main()