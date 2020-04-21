import urllib
import re
from const import URL
import requests



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
        else:    
            cur_message = cur_result['message']['text']
    if 'edited_message' in cur_result:
        cur_user = cur_result['edited_message']['chat']['username']
        cur_chat = cur_result['edited_message']["chat"]["id"]
        cur_message = cur_result['edited_message']['text']
    return cur_user, cur_chat, cur_message
