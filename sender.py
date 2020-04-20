import requests
from const import token
from protect import do_some_protection
import json
import time
import urllib

URL = "https://api.telegram.org/bot{}/".format(token)
LOGIN = False

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=300"
    if offset:
        url += "?offset={}".format(offset)
    updates = get_json_from_url(url)
    return updates

def get_last_update_id(updates):
    update_ids = []
    for update in updates['result']:
        update_ids.append(int(update['update_id']))
    return max(update_ids)

def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def get_last_chat_id_and_text(updates):
    #handle take photo
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    
    if 'text' in updates["result"][last_update]["message"]:
        text = updates["result"][last_update]["message"]["text"]
    else:
        text = 'this some but not message'
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def clean_history():
    updates = get_updates()
    chat_id = updates["message"]["chat"]["id"]
    message_ids = []
    for update in updates:
        message_ids.append(update['message']['message_id'])
    urls = []
    for message_id in message_ids:
        urls.append(URL+'deleteMessage?chat_id={}&message_id=P{}'.format(chat_id,message_id ))
    for url in urls:
        requests.get(url)
        time.sleep(0.1)

def echo_all(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_message(text, chat)
        except Exception as e:
            print(e)



def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)

if __name__ == "__main__":
    do_some_protection()
    main()
    #clean_history()
    

    
    
