import os
import json
import shutil




class Session(object):

    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.user_info = {'username':username,'password':password,'uploaded_pictures':[]}
        self.user_folder = self.create_user_folder()
        self.save_user_info()

    def save_user_info(self):
        with open(self.user_folder +'/{}.json'.format(self.username), 'w', encoding='utf-8') as f:
            json.dump(self.user_info, f, ensure_ascii=False, indent=4)

    def get_session_details(self):
        pass

    def create_user_folder(self):
        os.makedirs(os.getcwd()+'/session/'+self.username,exist_ok = True)
        return str(os.getcwd()+'/session/'+self.username)


    def clean_session(self):
        shutil.rmtree(self.user_folder, ignore_errors=True)