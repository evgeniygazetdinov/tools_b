import requests
import json
from lib.const import BACKEND_URL, URL
from lib.base import send_message
from urllib import request, parse
import os
import re


#describe methods for work with  api on dv24.website


def user_exist(username):
    url = BACKEND_URL+'user/exists/'+username+'/'
    response = requests.get(url)
    print(response.status_code)
    return True if response.status_code == 200 else False


def create_user(username,password):
    url = BACKEND_URL+'user/create/'
    body = {'username': username,'password': password}
    response =  requests.post(url,data=body)
    print(response.status_code)
    return True if response.status_code == 201 or response.status_code == 200 else False


def do_login(username,password,cur_chat,show_user_content=False):
    url = BACKEND_URL+'user/check_current/'
    with requests.session() as s:
        s.auth = (username, password)
        r = s.get(url)
        print(r.status_code)
        if r.status_code == 201 or r.status_code ==200:
            send_message('you authenticated',cur_chat)
            if show_user_content:
                return json.loads(r.text)
            return True
        else:
            return False



def upload_photo_on_server(filename,username,password):
    with open(os.getcwd()+'/'+filename,'rb') as img:
        #name_img= os.path.basename(path_img)
        files= {'image': (filename,img,'multipart/form-data') }
        with requests.Session() as s:
            s.auth = (username, password)
            r = s.post(BACKEND_URL+'photo/upload/',files=files)
            return True if r.status_code == 201 or r.status_code == 200 else False


def get_my_uploaded_photos():
    url = BACKEND_URL+'user/check_current/'
    with requests.session() as s:
        s.auth = (username, password)
        r = s.post(url)
        print(r.status_code)
        print(r.content)
        return True if r.status_code == 201 or r.status_code == 200 else False


def change_password(username,old_password,new_password):
    url = BACKEND_URL+'user/update/'
    body = {'old_password': old_password,'new_password': new_password}
    with requests.session() as s:
        s.auth = (username, old_password)
        response = s.put(url,body)
        print(response.content)
        return True if response.status_code == 201 or response.status_code == 200 else False

      
def extract_name_from_content_dis(cd):
    if not cd:
           return 'None'
    fname = re.findall('filename=(.+)', cd)
    return 'None.jpg' if len(fname) == 0 else fname[0]


def upload_photo_from_telegram_and_get_path(url):
    r = requests.get(url, allow_redirects=True)
    filename = extract_name_from_content_dis(r.headers.get('content-disposition'))
    open(filename, 'wb').write(r.content)
    return filename, os.getcwd()+'/'+filename
