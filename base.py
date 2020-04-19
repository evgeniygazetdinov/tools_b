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
    clean_password = div_password(password)
    if re.match(r'[mypassword=A-Za-z0-9@#$%^&+=]{8,}', clean_password):
        return True
    else:
        send_message('try another password',cur_chat)