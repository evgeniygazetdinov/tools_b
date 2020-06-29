import requests
import json
from lib.const import BACKEND_URL, URL
from lib.base import send_message
from urllib import request, parse
import os
import re


#describe methods for work with  api on dv24.website
#refactir on class

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


def do_login(username,password,show_user_content=False):
    url = BACKEND_URL+'user/check_current/'
    with requests.session() as s:
        s.auth = (username, password)
        r = s.get(url)
        try:
            print(r.status_code)
            print(r.text)
        except:
            pass
        if r.status_code == 201 or r.status_code ==200:
            if show_user_content:
                return json.loads(r.text)
            return True
        else:
            return False




def upload_photo_on_server(filename,username,password,show_user_content=False):
    with open(os.getcwd()+'/'+filename,'rb') as img:
        #name_img= os.path.basename(path_img)
        files= {'image': (filename,img,'multipart/form-data') }
        with requests.Session() as s:
            s.auth = (username, password)
            r = s.post(BACKEND_URL+'photo/upload/',files=files)
            if r.status_code == 201 or r.status_code ==200:
                if show_user_content:
                    return json.loads(r.text)
                return True
            else:
                return False


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


def change_delete_time(username,password,new_time):
    url = BACKEND_URL+'user/update_delete_time/'
    body = {'new_time': new_time}
    with requests.session() as s:
        s.auth = (username, password)
        response = s.put(url,body)
        print(response.content)
        return True if response.status_code == 201 or response.status_code == 200 else False


def change_photoposition(username, password, image_name, latitude, longitude, show_user_content=False):
    url = BACKEND_URL+'photo/change_photoposition/'
    body = {'image': image_name,'latitude': latitude,
    'longitude':longitude}
    with requests.session() as s:
        s.auth = (username, password)
        r= s.post(url,body)
        if r.status_code == 201 or r.status_code ==200:
            if show_user_content:
                return json.loads(r.text)
            return True
        else:
            print(r.text)
            return False
          

def change_description(username, password, image_name, description, show_user_content=False):
    url = BACKEND_URL+'photo/change_description/'
    body = {'image': image_name,'description':description}
    with requests.session() as s:
        s.auth = (username, password)
        r= s.post(url,body)
        if r.status_code == 201 or r.status_code ==200:
            if show_user_content:
                return json.loads(r.text)
            return True
        else:
            print(r.text)
            return False


def add_photos_to_upload_list(username,password,image_string,show_user_content=False):
    url = BACKEND_URL+'photo/to_upload_list/'
    body = {'photos': image_string}
    with requests.session() as s:
        s.auth = (username, password)
        r= s.post(url,body)
        if r.status_code == 201 or r.status_code ==200:
            if show_user_content:
                return json.loads(r.text)
            return True
        else:
            print(r.text)
            return False
