import requests
from const import token
from protect import do_some_protection
import json
import time 
from requests.auth import HTTPBasicAuth
URL ='https://api.telegram.org/bot{}/'.format(token)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode('utf-8')
    return content


def get_json_from_url(url):
    content = get_url(url)
    updates = json.loads(content)
    return updates


def get_updates(offset=None):
    url = URL +'getUpdates?timeout=100'
    if offset:
        url += '&offset={}'.format(offset)
    updates_in_json = get_json_from_url(url)
    return updates_in_json

def get_last_update_id(updates):
    update_ids = []
    for update in updates['result']:
        update_ids.append(int(update['update_id']))
    return max(update_ids)

def echo_all(updates):
    for update in updates['result']:
        try:
            text = update['message']['text']
            chat = update['message']['chat']['id']
            resp = requests.get('https://ya.ru')
            print(resp.text)
            send_message('fsdfsd', chat)
        except Exception as e:
            print(e)
            

def send_message(text, chat_id):
    url = URL + 'sendMessage?text={}&chat_id={}'.format(text,chat_id)
    get_url(url)

def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates['result']) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(1)



if __name__ == '__main__':
    do_some_protection()
    main()
