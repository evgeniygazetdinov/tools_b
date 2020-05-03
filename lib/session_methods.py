import glob
import os

PATH = os.getcwd()+'/session/'

def json_to_dict(path):
    with open(path) as json_file:
        data = json.load(json_file)
        return data


def check_last_updated_file():
    #check_last_updated_folder
    list_of_files = glob.glob(PATH+'/*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def get_current_user():
    file = check_last_updated_file()
    user = os.path.basename(file)
    return str(user)


def get_user_action(user):
    user_path = PATH+'/'+user+'/'+user+'.json'
    user_dict = json_to_dict(user_path)
    return user_dict
    

def notify_user(chat):
    pass    