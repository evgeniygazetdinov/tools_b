import json
import os
from lib.const import URL
import aiohttp
import asyncio

#here save user and bot message id into file and methods for bring this
path =os.getcwd()+'/session/bot_action.json'

def get_path(user=False):
    path =os.getcwd()+'/session/bot_action.json'
    if user:
        path = os.getcwd()+'/session/{}/user_action.json'.format(user)
    return path

def path_for_user_or_bot(user,is_user=False):
    return get_path(user) if is_user else get_path()

def get_data_by_path(user,is_user=False):
    path = path_for_user_or_bot(user,is_user=False)  
    if os.path.exists(path):
        with open(path,'r') as json_file:
            data = json.load(json_file)
            return  data if data is not None else store_action(path,{user:[]});{user:[]}
    else:
        data = {user:[]}
        store_action(path,data)
        return data


def store_action(path,result):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

def data_from_storage(path,bot_action_by_user=False):
    if bot_action_by_user:
        pass

def save_bot_action(content):
    content = content.json()
    if len(content["result"]) != 0:
        cur_result = content["result"]
        #it's bot action 
        if 'message_id' in cur_result:
            if cur_result['from']['is_bot'] :
                if 'username' in cur_result['chat']:
                    user = cur_result['chat']['username']
                else:
                    user = cur_result['chat']['first_name']+cur_result['chat']['last_name']
                message = content['result']['message_id']
                data = get_data_by_path(user)
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
                from_ = res['message']['from']
                if 'username' in from_:
                    user = from_['username']
                else:
                    user = from_['first_name']+from_['last_name']
                data = get_data_by_path(user,is_user=True)
                if user in data:
                    data[user].append(message)
                else:
                    data[user] = []
                store_action(path,data)
                print('store user action')



def extract_ids(username):
    message_ids = []
    bot_path = get_path()
    user_path = get_path(username)
    user_data = data_from_storage(user_path)
    bot_data = data_from_storage(bot_path,username)
    if username in bot_data:
        if username in user_data:
            for message_id in bot_data[username].values():
                message_ids.append(message_id)
            for message_id in user_data[username].values():
                message_ids.append(message_id)
    return list(set(message_ids))


def create_links_for_delete(session,username):
    links = []
    chat_id= session.get()
    message_ids = extract_ids(username)
    for message_id in message_ids:
        links.append(URL+'/deletemessage?message_id={1}&chat_id={2}'.format(message_id,chat_id))
    return links



async def delete_message(url):
  async with aiohttp.ClientSession() as session:
      async with session.get(url) as resp:
          text = await resp.status_code
          print('Url{url}, status {text}'.format(url,text))


def clean_history():
    links = create_links_for_delete(session,username)
    futures = [delete_message(link) for link in links ]
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(asyncio.wait(futures))

