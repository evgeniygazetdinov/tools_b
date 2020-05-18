import time 
from lib.const import URL
from lib.base import send_message
from lib.history import create_links_for_delete,clean_history, delete_user_ids_from_bot_actions, store_action, get_path
from lib.active_users import remove_active_users
#file has method for be executed with session/ each push button will  be check user time and store message id for clean history
import requests
import json
import urllib
import os
menu_keyboard = {
    'one_time_keyboard': True,
    'keyboard': [ ['create_profile'], ['login'] ,['help']]
}

#so ugly
def send_raw_message(text, chat_id, reply_markup=None):
    #text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage"
    data = {'chat_id':chat_id,'text':text}
    if reply_markup:
       data['reply_markup'] = json.dumps(reply_markup)
    response = requests.get(url,data)
    #store raw response messageid
    context= response.json()
    if 'result' in context:
        mes_id = context['result']['message_id']
        if 'username' in context['result']['chat']:
            user = context['result']['chat']['username']
        else:
            user = context['result']['chat']['first_name'] + context['result']['chat']['last_name']
        path = get_path()
        if os.path.exists(path):
            with open(path,'r') as json_file:
                data = json.load(json_file)
        #data-dict empty
        if (not data):
            data[user]=[mes_id]
            print('*'*10)
            print(data)
            print(mes_id)
            print('*'*10)
        else:
            print('*'*10)
            data[user].append(mes_id)
            print(data)
            print(mes_id)
            print('*'*10)
           
        store_action(path,data)



    #push message_id into user_list)))

    


#executed on push button
def check_user_actions(cur_user,session):
    #just call and wait 60 second /if he passed clean history and clean session
    minute = 10
    begin = 0
    while session.get_user_info_value('pushed_button'):
        begin+=1
        time.sleep(1)
        print(begin)
        #check_user_folder
        if begin  == minute:
            print('time is over')
            send_message('60 second passed',session.get_user_info_value('cur_chat') )
           
           
            clean_history(session,session.username)
            delete_user_ids_from_bot_actions(session.username)
            remove_active_users(session.username)
            #remove_from_bot
            
            send_raw_message('Choose your variant',session.get_user_info_value('cur_chat'),menu_keyboard)
            session.clean_session()
            
            break