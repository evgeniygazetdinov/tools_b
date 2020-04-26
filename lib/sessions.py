import os
import json
import shutil




class Session(object):

    def __init__(self,username,password=False):
        self.username = username
        self.password = password
        #check_folder
        #exists load 
        #else create
        if os.path.exists(os.getcwd()+'/session/'+self.username):
            self.user_folder = os.getcwd()+'/session/'+self.username
            self.user_info = self.get_session_details()

        else:
            self.user_info = {'username':username,'password':password,
            'state': {'login': False, 'created': False,'upload': False}}
            self.user_folder = self.create_user_folder()
            self.save_user_info()

    def update_state_user(self,state,value,password=False):
        self.user_info['state'][state] = value
        if password:
            self.user_info['password'] = password
        self.save_user_info()
        print(self.user_info)

    def save_user_info(self):
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

