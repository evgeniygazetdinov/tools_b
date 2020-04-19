import requests
import json

BACKEND_URL = 'https://dv24.website/'


def user_exist(username):
    url = BACKEND_URL+'user/exists/'+username+'/'
    response = requests.get(url)
    if response.status_code == '200':
        return True
    else:
        return False


def do_login(username,password):
    pass

def create_user(username,password):
    pass

def upload_photo(photo):
    pass

def get_my_uploaded_photos():
    pass