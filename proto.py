import json
import requests
import time
import urllib
from const import  URL
from protect import do_some_protection
from backend_methods import user_exist,create_user
from base import check_it_is_password, send_message, get_url, find_user_message_chat




login_items = ['my_uploads','change_password', 'instructions','end_sessions']
menu_items = ['create_profile','login','help']
password_item = ['put password']





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


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) != 0:
            last_update_id = get_last_update_id(updates) + 1 
            #check here picture or message
            cur_user, cur_chat, cur_message = find_user_message_chat(updates['result'])
            if cur_message == '/start':
                send_message("hello this photohosting bot please create profile or login",cur_chat)
                keyboard = build_keyboard(menu_items)
                send_message('Choose your variant', cur_chat, keyboard)
            else:
                if cur_message =='login':
                    exist = user_exist(cur_user)
                    if exist:
                        send_message('PUT YOUR PASSWORD', cur_chat)
                        send_message('mypassword=YOUR PASSWORD MUST BE HERE', cur_chat)
                        if re.match(r'[mypassword=A-Za-z0-9@#$%^&+=]{8,}', cur_message):
                            password = div_password(cur_message)
                            login = do_login(cur_user,password,cur_chat)
                            if login: 
                                keyboard = build_keyboard(login_items)
                                send_message('Choose your variant', cur_chat, keyboard)
                        else:
                            send_message('some thing bad with your password try again', cur_chat)
                            keyboard = build_keyboard(menu_items)
                            send_message('Choose your variant', cur_chat, keyboard)
                    else:
                        send_message('your user exist to our database choose create profile for create', cur_chat)
                        keyboard = build_keyboard(menu_items)
                        send_message('Choose your variant', cur_chat, keyboard)
                if cur_message == 'create_profile':
                    send_message('YOUR telegram username it is login', cur_chat)
                    send_message('PUT YOUR PASSWORD', cur_chat)
                    send_message('mypassword=YOUR PASSWORD MUST BE HERE', cur_chat)
    
                if cur_message == 'help':
                    send_message('help MUST BE HERE', cur_chat)
                    keyboard = build_keyboard(menu_items)
                    send_message('Choose your variant', cur_chat, keyboard)
                else:
                    if re.match(r'[mypassword=A-Za-z0-9@#$%^&+=]{8,}', cur_message):
                        password = div_password(cur_message)
                        print('true password')
                        success = create_user(cur_user,password)
                        if success:
                            send_message('profile was created please try login', cur_chat)
                            keyboard = build_keyboard(menu_items)
                            send_message('Choose your variant', cur_chat, keyboard)
                        else:
                            send_message('some thing bad with server type exit for confirm'.format(cur_user), cur_chat)
                    else:
                        send_message('some thing bad with your password try again', cur_chat)
                        keyboard = build_keyboard(menu_items)
                        send_message('Choose your variant', cur_chat, keyboard)
                #create_new_user_handler(cur_user)
        time.sleep(0.5)



if __name__ == '__main__':
    do_some_protection()
    main()