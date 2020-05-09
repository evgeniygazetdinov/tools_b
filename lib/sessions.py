
import os
import json
import shutil
from datetime import datetime
import time




class Session(object):
    def __init__(self, username, chat, message_id, password=False):
        self.username = username
        self.password = password
        self.cur_chat = chat
        self.message_id = message_id
        #check_folder
        #exists load 
        #else create
        if os.path.exists(os.getcwd()+'/session/'+self.username):
            self.user_folder = os.getcwd()+'/session/'+self.username
            self.user_info = self.get_session_details()
            self.save_user_info()
        else:
            self.user_info = {'username':username,'password':password,
            'state': {'login': False, 'created': False,'upload': False,'change_password':False},
            'changer':{'old_password':False,'new_password':False},
            'last_action':datetime.now().strftime('%Y-%m-%d %H:%M'),
            'pushed_button': False,'cur_chat': self.cur_chat,'message_id':self.message_id}
            self.user_folder = self.create_user_folder()
            self.save_user_info()

    def update_user_info(self,value,condition):
        self.user_info[value] = condition
        self.save_user_info()
    
    
    def update_last_action(self):
        self.user_info['last_action'] = datetime.now().strftime('%Y-%m-%d %H:%M')


    def update_state_user(self,state,value,password=False):
        self.update_last_action()
        self.user_info['state'][state] = value
        if password:
            self.user_info['password'] = password
        self.save_user_info()
        print(self.user_info)

    def get_user_info_value(self,value):
        self.update_last_action()
        return self.user_info[value]

    def save_to_user_history():
        with open(self.user_folder +'/history.json', 'w+', encoding='utf-8') as f:
            json.dump(self.user_info, f, ensure_ascii=False, indent=4)

    def save_user_info(self):
        self.update_last_action()
        #self.save_to_user_history()
        with open(self.user_folder +'/{}.json'.format(self.username), 'w', encoding='utf-8') as f:
            json.dump(self.user_info, f, ensure_ascii=False, indent=4)

    def get_session_details(self):
        with open(self.user_folder +'/{}.json'.format(self.username)) as json_file:
            data = json.load(json_file)
            return data

    def create_user_folder(self):
        os.makedirs(os.getcwd()+'/session/'+self.username,exist_ok = True)
        return str(os.getcwd()+'/session/'+self.username)


    def clean_session(self):
        shutil.rmtree(self.user_folder, ignore_errors=True)

