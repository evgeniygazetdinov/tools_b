import glob
import os
from lib.base import send_message
import json


PATH = os.getcwd()+'/session'


def looking_for_changes():
    last_updaten = check_last_updated_file()
        #check algoritm there last string changes if change file
       



def json_to_dict(path):
    with open(path) as json_file:
        data = json.load(json_file)
        return data


def check_last_updated_file():
    #check_last_updated_folder
    list_of_files = glob.glob(PATH+'/*') 
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def get_user_from_session():
    file = check_last_updated_file()
    user = os.path.basename(file)
    return str(user)


def get_action_from_session(user):
    user_path = PATH+'/'+user+'/'+user+'.json'
    user_dict = json_to_dict(user_path)
    return user_dict['cur_chat'],user_dict
    
def get_current_chat():
    pass


def notify_user(chat):
    pass    