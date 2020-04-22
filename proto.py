import json
import requests
import time
import urllib
import re
from lib.sessions import Session
from lib.const import  URL
from lib.protect import do_some_protection
from lib.backend_methods import user_exist,create_user
from lib.base import  (send_message, get_url, find_user_message_chat,
                  div_password, build_keyboard, get_json_from_url,get_last_update_id,
                  get_updates, get_updates, get_last_chat_id_and_text)


login_items = ['my_uploads','change_password', 'instructions','end_sessions']
menu_items = ['create_profile','login','help']
password_item = ['put password']



def main_flow():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) != 0:
            #init section
            last_update_id = get_last_update_id(updates) + 1 
            cur_user, cur_chat, cur_message = find_user_message_chat(updates['result'])
            login_keyboard = build_keyboard(login_items)
            menu_keyboard = build_keyboard(menu_items)
            user_session = Session(cur_user)
            if cur_message == '/start':
                send_message("hello this photohosting bot please create profile or login",cur_chat)
                send_message('Choose your variant', cur_chat, menu_keyboard)


            if cur_message =='login':
                exist = user_exist(cur_user)
                if exist:
                    send_message('PUT YOUR PASSWORD', cur_chat)
                    send_message('mypassword=YOUR PASSWORD MUST BE HERE', cur_chat)
                    user_session.update_state_user('login','in_process')
                else:
                    send_message('Your user not created in system -> choose create profile', cur_chat)
                    send_message('Choose your variant', cur_chat, menu_keyboard)
                    
            #add session contidion        
            if re.match(r'[mypassword=A-Za-z0-9@#$%^&+=]{8,}', cur_message) and  user_session.user_info['state']['login'] == 'in_process':
                password = div_password(cur_message)
                login = do_login(cur_user,password,cur_chat)
                if login: 
                    send_message('Choose your variant', cur_chat, login_keyboard)
                    user_session.update_state_user('login',True,password)
                else:
                    send_message('something bad with your password try again', cur_chat)
                    send_message('Choose your variant', cur_chat, menu_keyboard)


            if cur_message == 'create_profile':
                exist = user_exist(cur_user)
                if exist:
                    send_message('your user already exists .try to login', cur_chat)
                    send_message('Choose your variant', cur_chat, menu_keyboard)
                
                else:
                    send_message('YOUR telegram username it is login', cur_chat)
                    send_message('PUT YOUR PASSWORD', cur_chat)
                    send_message('mypassword=YOUR PASSWORD MUST BE HERE', cur_chat)
                    user_session.update_state_user('created','in_process')
                    
             #add session in condition   
            if re.match(r'[mypassword=A-Za-z0-9@#$%^&+=]{8,}', cur_message) and user_session.user_info['state']['created'] == 'in_process':
                password = div_password(cur_message)
                success = create_user(cur_user,password)
                if success:
                    send_message('profile was created please try login', cur_chat)
                    send_message('Choose your variant', cur_chat, menu_keyboard)
                    user_session.update_state_user('created',True,password)
                else:
                    send_message('something bad with server.Try again later'.format(cur_user), cur_chat)
                    send_message('Choose your variant', cur_chat, menu_keyboard)

            if cur_message == 'help':
                send_message('help MUST BE HERE', cur_chat)
                send_message('Choose your variant', cur_chat, menu_keyboard)
        time.sleep(0.5)



if __name__ == '__main__':
    do_some_protection()
    main_flow()
