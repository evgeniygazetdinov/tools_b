import time 
from lib.const import URL
from lib.base import send_message
from lib.history import create_links_for_delete,clean_history
from lib.active_users import remove_active_users
#file has method for be executed with session/ each push button will  be check user time and store message id for clean history
import requests


menu_items = ['create_profile','login','help']

def send_raw_message(text, chat_id, reply_markup=None):
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    response = requests.get(url)
    


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
            remove_active_users(session.username)
            clean_history(session,session.username)
            #remove_from_bot
            session.clean_session()
            break