import json
import os

#here save user and bot message id into file and methods for bring this
path =os.getcwd()+'/session/bot_action.json'

def get_path(user=False):
    path =os.getcwd()+'/session/bot_action.json'
    if user:
        path = os.getcwd()+'/session/{}/user_action.json'.format(user)
    return path


def get_data(user,is_user=False):
    data = {user:[]}
    path = get_path()
    if is_user:
        path = get_path(user)
    if os.path.exists(path):
        with open(path,'r') as json_file:
            data = json.load(json_file)
            if data is  None:
                store_action(path,{user:[]})
                return {user:[]}
    store_action(path,data)
    return data


def store_action(path,result):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)



def save_bot_action(content):
    content = content.json()
    if len(content["result"]) != 0:
        cur_result = content["result"]
        #it's bot action 
        if 'message_id' in cur_result:
            if cur_result['from']['is_bot'] :
                user = cur_result['chat']['username']
                message = content['result']['message_id']
                data = get_data(user)
                if user in data:
                    data[user].append(message)
                    store_action(path,data)
                    print('store bot action')
                else:
                    print(data)
                    data[user]=[]
                    store_action(path,data)
        elif  isinstance(content['result'], list):
        #it's user
            res = content['result'][0]
            if  res["message"]["from"]["is_bot"] == False:
                message =res['message']['message_id']
                user = res['message']['from']['username']
                data = get_data(user,is_user=True)
                data[user].append(message)
                store_action(path,data)
                print('store user action')


def create_links_for_delete(username):
    message_ids = []
    bot_path = get_path()
    user_path = get_path(username)
    


def clean_history():
    pass