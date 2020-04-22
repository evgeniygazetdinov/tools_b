import requests
import json
from lib.const import BACKEND_URL, URL
from lib.base import send_message
from urllib import request, parse




#describe methods for work with  api on dv24.website


def user_exist(username):
    url = BACKEND_URL+'user/exists/'+username+'/'
    response = requests.get(url)
    print(response.status_code)
    if response.status_code == 200:
        return True
    else:
        return False


def create_user(username,password):
    url = BACKEND_URL+'user/create/'
    body = {'username': username,'password': password}
    response =  requests.post(url,data=body)
    print(response.status_code)
    if response.status_code == 201 or response.status_code == 200:
        return True
    else:
        return False





def do_login(username,password,cur_chat):
    url = BACKEND_URL+'user/check_current/'
    with requests.session() as s:
        s.auth = (username, password)
        r = s.get(url)
        print(r.status_code)
        print(r.content)
        if r.status_code == 201 or r.status_code ==200:
            send_message('you authenticated',cur_chat)
            return True
        else:
            return False



def upload_photo(photo):
    session = requests.Session()

    files = {'image': open('1.jpeg', 'rb')}
    with open(os.getcwd()+'/1.jpeg','rb') as img:
        #name_img= os.path.basename(path_img)
        files= {'image': ('1.jpeg',img,'multipart/form-data') }
        with requests.Session() as s:
            s.auth = ('vitor2', '2xaxaxa2')
            r = s.post('https://dv24.website/photo/upload/',files=files)
            print(r.status_code)


def get_my_uploaded_photos():
    url = BACKEND_URL+'user/check_current/'
    with requests.session() as s:
        s.auth = (username, password)
        r = s.post(url)
        print(r.status_code)
        print(r.content)
        if r.status_code == 201 or r.status_code ==200:
            return True
        else:
            return False
