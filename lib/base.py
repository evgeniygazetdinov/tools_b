import urllib
import re
from lib.const import URL, token
import requests
import json


menu_items = ['create_profile','login','help']
get_file = 'https://api.telegram.org/bot/getFile?file_id='


def clean_patern(cur_message):
    #refactor now
    #template for 
    #variable
    link = ''
    if re.match(r'photo=', cur_message):
        link = cur_message.split('photo=')
    if re.match(r'document=', cur_message):
        link = cur_message.split('document=')
    if re.match(r'download_link=', cur_message):
        link = cur_message.split('download_link=')
    if re.match(r'oldpassword=', cur_message):
        link = cur_message.split('oldpassword=')

    if re.match(r'newpassword=', cur_message):
        link = cur_message.split('newpassword=')
    return link[-1]



def get_link_for_update_photo(token,file_id_link):
    #check_link with re photo or documnet
    #clean
    #get request by this
    #get file path
    #insert file path into url
    #return link for downloadand  user_session.user_info['state']['login'] == 'in_proces

    url =clean_patern(file_id_link)
    file_id = requests.get(url)
    data = json.loads(file_id.text)
    file_path = data['result']['file_path']
    upload_path = 'download_link=https://api.telegram.org/file/bot{}/{}'.format(token, file_path)
    return upload_path



def build_keyboard(items):
    keyboard = [[item]for item in items]
    reply_markup = {'keyboard':keyboard, 'one_time_keyboard':True}
    return json.dumps(reply_markup)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def div_password(password):
    remove_block = password.split('=')
    return remove_block[-1]


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)



def check_it_is_password(password,cur_chat):
    if re.match(r'mypassword=A-Za-z0-9@#$%^&+=]{8,}', password):
        return div_password(password)
    else:
        send_message('try another password',cur_chat)
        return False


def find_user_message_chat(results):
    cur_result = results[0]
    if 'message' in cur_result:
        cur_user = cur_result['message']['chat']['username']
        cur_chat = cur_result['message']["chat"]["id"]
        if 'sticker' in cur_result['message']:
            cur_message = 'sticker'
            send_message('nice sticker',cur_chat)
            menu_keyboard = build_keyboard(menu_items)
            send_message('choose variant',cur_chat,menu_keyboard)
        elif 'photo' in cur_result['message']:
            file_id_link = 'photo='+'https://api.telegram.org/bot{}/getFile?file_id={}'.format(token, cur_result['message']['photo'][-1]['file_id'])
            cur_message = get_link_for_update_photo(token,file_id_link)
            print(cur_message)

        elif 'document' in cur_result['message']:
            file_id_link = 'document='+'https://api.telegram.org/bot{}/getFile?file_id={}'.format(token, cur_result['message']['document']['thumb']['file_id'])
            cur_message = get_link_for_update_photo(token,file_id_link)
            print(cur_message)
        else:
            cur_message = cur_result['message']['text']
    if 'edited_message' in cur_result:
        cur_user = cur_result['edited_message']['chat']['username']
        cur_chat = cur_result['edited_message']["chat"]["id"]
        cur_message = cur_result['edited_message']['text']

    return cur_user, cur_chat, cur_message



def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)



def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)



def delete_message(chat_id,message_id):
    url = URL + '/deletemessage?message_id={1}&chat_id={2}'.format(message_id, chat_id)
    response = requests.get(url)
    if response.status_code == 201 or response.status_code ==200:
        return True
    else: 
        return False
