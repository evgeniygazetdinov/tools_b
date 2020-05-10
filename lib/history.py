import json
import os

#here save user and bot message id into file and methods for bring this
path =os.getcwd()+'/session/bot_action.json'


def store_bot_action(result):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


def get_data(user):
    data = {user:[]}
    if os.path.exists(path):
        with open(path,'r') as json_file:
            data = json.load(json_file)
            if data is  None:
                store_bot_action({user:[]})
                return {user:[]}
    store_bot_action(data)
    return data


def save_bot_action(content):
    content = content.json()
    print(content)
    if len(content["result"]) != 0:
        cur_result = content["result"]
        if 'message_id' in cur_result:
            if cur_result['from']['is_bot'] :
                user = cur_result['chat']['username']
                message = content['result']['message_id']
                data = get_data(user)
                data[user].append(message)
                store_bot_action(data)
                print(data)
                print('action saved')


def clean_history():
    pass