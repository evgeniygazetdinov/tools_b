import requests
import json
from const import BACKEND_URL




def user_exist(username):
    url = BACKEND_URL+'user/exists/'+username+'/'
    response = requests.get(url)
    if response.status_code == '200':
        return True
    else:
        return False


def create_user(username,password):
    #add_headers
    url = BACKEND_URL+'user/create/'
    payload = {'username': username,'password': password}
    response = requests.post(url,data = payload)
    print(response.status_code)
    if response.status_code == '200':
        return True
    else:
        return False

def do_login(username,password):
    pass


def upload_photo(photo):
    pass

def get_my_uploaded_photos():
    pass