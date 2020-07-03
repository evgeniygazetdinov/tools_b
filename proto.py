# -*- coding: utf-8 -*-
import sys
print(sys.getdefaultencoding())
import json
import unicodedata
import os
import requests
import time
import urllib
import re
import sys
import datetime
import threading
from multiprocessing import Process,current_process,cpu_count,active_children
from lib.photo_display_methods import (get_uploaded_photos_from_response,get_newest_upload_list,
                                    delete_viewed_photos,clean_empty_uploadlists)
from lib.sessions import Session
from lib.session_methods import check_user_actions,send_raw_message, hide_tracks
from lib.const import  URL
from lib.buttons import menu_items, login_items, kick_out, yes_no_items, under_upload_menu
from lib.protect import do_some_protection
from lib.active_users import get_active_users, save_users_state, push_active_users, remove_active_users
from lib.backend_methods import (change_password, user_exist, create_user,
                            upload_photo_from_telegram_and_get_path,
                            do_login, upload_photo_on_server, change_delete_time,
                            change_photoposition, change_description,
                            add_photos_to_upload_list)
from lib.base import  (build_keyboard,clean_patern, send_message, send_location, get_url, find_user_message_chat,
                  div_password, build_keyboard, get_json_from_url,get_last_update_id,
                  get_updates, get_updates, get_last_chat_id_and_text, telegram_clean_history,
                  make_filestring_for_request )


def check_telegram_updates():
        last_update_id = None
        args = []
        while True:
            try:
                updates = get_updates(last_update_id)
            except KeyboardInterrupt:
                print('Interrupted')
                sys.exit(0)
            if len(updates["result"]) != 0:
                    #init section
                last_update_id = get_last_update_id(updates) + 1
                cur_user, cur_chat, cur_message,message_id = find_user_message_chat(updates['result'])
                push_active_users(cur_user)
                login_keyboard = build_keyboard(login_items)
                menu_keyboard = build_keyboard(menu_items)
                user_session = Session(cur_user,cur_chat,message_id)
                if cur_message == '/start':
                    send_message("Привет это бот фотохостинга",cur_chat)
                if cur_message:
                    #remove active threads before
                    #here save user_message_info session
                    active_users = get_active_users()
                    for p in active_children():
                        if int(p.name) in active_users['users']:
                            if int(p.name) == cur_user:
                                p.terminate()
                                remove_active_users(cur_user)
                        else:
                            continue
                    user_session.update_user_info('pushed_button',True)
                    #BEGIN new counter user action
                    thread2 = Process(name ="{}".format(cur_user),target=check_user_actions,args = (cur_user, user_session))
                    thread2.start()                
                if user_session.user_info['state']['login'] == True:             
                    if user_session.user_info['state']['upload'] == 'in_process' or \
                        user_session.user_info['state']['change_password'] == 'in_process' or \
                        user_session.user_info['state']['change_time_check_updates'] == 'in_process' or \
                        user_session.user_info['state']['upload']  or\
                        user_session.user_info['photo_position']['longitude'] or\
                        user_session.user_info['photo_position']['latitude'] or\
                        cur_message =='загрузить фото' or \
                        cur_message == 'инструкции' or \
                        cur_message == 'сменить пароль' or \
                        cur_message == 'сменить время чистки':
                            send_raw_message('👌', cur_chat, kick_out)
                    elif cur_message == 'мои загрузки' or user_session.user_info['on_check_photos']:
                       send_message('выберите вариант', cur_chat, under_upload_menu)
                    else:
                        send_message('выберите вариант', cur_chat, login_keyboard)
                    if cur_message == 'назад' and  user_session.user_info['on_check_photos']:
                        #inside myuploads
                        user_session.user_info['on_check_photos'] = False
                        user_session.save_user_info()

                    if cur_message == 'назад':
                        user_session.reset_login_session()
                        send_message('выберите вариант', cur_chat, login_keyboard)
                    
                    
                ###############end_session##################################################
                    if cur_message =='завершить сессию':
                        send_message('Досвидания', cur_chat)                      
                        hide_tracks(user_session)
                        user_session.clean_session()
                #############upload_image###############################################
                    if cur_message =='загрузить фото':
                        send_message('Перетяните или выберете изоображение', cur_chat)
                        user_session.update_state_user('upload','in_process')
                    if re.match(r'download_link=', cur_message) and user_session.user_info['state']['upload'] == 'in_process':
                        url = clean_patern(cur_message)
                        filename,path_file = upload_photo_from_telegram_and_get_path(url)
                        sucess_upload = upload_photo_on_server(filename,user_session.user_info['login_credentials']['username'],user_session.user_info['login_credentials']['password'],True)
                        os.remove(path_file)
                        user_session.save_user_info()
                        if sucess_upload:
                            send_message('Добавьте геопозицию к фото',cur_chat)
                            filename = (str(sucess_upload['image']).split('/media/'))[-1]
                            if isinstance(filename, str):

                                user_session.user_info['uploaded_photos'].append(filename)
                                user_session.user_info['photo_position']['filename'] = filename
                                user_session.update_state_user('upload','on_geoposition')
                            
                    elif re.match(r'location=',cur_message) and user_session.user_info['state']['upload'] == 'on_geoposition':
                        #remove 'location=' from str and converting to dict
                        location_str = (clean_patern(cur_message)).replace("\'", "\"")
                        location = json.loads(location_str)
                        position = change_photoposition(user_session.user_info['login_credentials']['username'],
                        user_session.user_info['login_credentials']['password'],
                        user_session.user_info['photo_position']['filename'], 
                        location['longitude'],
                        location['latitude'])
                        user_session.update_state_user('upload','on_description')
                        if position:
                            send_message('Геоданные добавлены', cur_chat)                      
                        else:
                            send_message('Сервер недоступен.Попробуйте позже', cur_chat)
                        send_message('Добавьте описание к фото', cur_chat)
                    elif user_session.user_info['state']['upload'] == 'on_description':
                        description = change_description(user_session.user_info['login_credentials']['username'],
                        user_session.user_info['login_credentials']['password'],
                        user_session.user_info['photo_position']['filename'],
                        cur_message) 
                        if description:
                            send_message('Описание  добавлено', cur_chat)
                            
                        else:
                            send_message('Сервер недоступен.Попробуйте позже', cur_chat)
                        send_message('Перетяните или выберете изоображение или нажмите назад для выхода', cur_chat)
                        user_session.update_state_user('upload','in_process')
                    elif cur_message == 'назад':
                        if len(user_session.user_info['uploaded_photos']) != 0 :
                            files = make_filestring_for_request(user_session.user_info['uploaded_photos'])
                            add_photos_to_upload_list(user_session.user_info['login_credentials']['username'],
                        user_session.user_info['login_credentials']['password'],files,True)
                ###########my_uploads#########################################

                    elif cur_message == 'мои загрузки':
                        user_session.user_info['on_check_photos'] = True
                        user_session.save_user_info()
                    elif cur_message == 'веcь список':
                        content = do_login(user_session.user_info['login_credentials']['username'],user_session.user_info['login_credentials']['password'],show_user_content=True)
                        clean_empty_uploadlists(user_session.user_info['login_credentials']['username'],user_session.user_info['login_credentials']['password'],content)
                        #store content to session and clean empty upload list  for right display photos
                        
                        values = get_uploaded_photos_from_response(content)
                        for key,value in values.items():
                           number= range(len(value))
                           send_message("""список {}\n{}""".format(key,value),cur_chat,under_upload_menu)
                    elif cur_message == 'новый список':
                        
                        content = do_login(user_session.user_info['login_credentials']['username'],user_session.user_info['login_credentials']['password'],show_user_content=True)
                        clean_empty_uploadlists(user_session.user_info['login_credentials']['username'],user_session.user_info['login_credentials']['password'],content)
                        #store content to session and clean empty upload list  for right display photos
                        user_session.put_user_photos_to_session(content)
                        print(user_session.user_info['photos_from_requests'])
                        values = get_newest_upload_list(content)
                        for key,value in values.items():
                            send_message("""список {}\n{}""".format(key,value),cur_chat,under_upload_menu)
                    elif cur_message == 'удалить просмотренные':
                        content = do_login(user_session.user_info['login_credentials']['username'],user_session.user_info['login_credentials']['password'],show_user_content=True)
                        clean_empty_uploadlists(user_session.user_info['login_credentials']['username'],user_session.user_info['login_credentials']['password'],content)
                        #store content to session and clean empty upload list  for right display photos
                        viewed_photos = delete_viewed_photos(user_session.user_info['login_credentials']['username'],user_session.user_info['login_credentials']['password'],content)
                        for key,value in viewed_photos.items():
                            send_message('удалено  \n по ссылке {} \n просмотры{}'.format(key,value['views']),cur_chat)
                        send_message('итого {}'.format(len(viewed_photos)),cur_chat)
                    
                    
                    
                   
                    
        
                        

                ##########change password######################################
                    elif cur_message =='сменить пароль':
                        send_message('Введите текущий пароль', cur_chat)
                        user_session.user_info['changer']['old_password'] = 'in_process'
                        user_session.update_state_user('change_password','in_process')
                    elif user_session.user_info['changer']['old_password'] == 'in_process':
                        if cur_message == user_session.user_info['login_credentials']['password']:
                            user_session.user_info['changer']['old_password'] = cur_message
                            user_session.user_info['changer']['new_password'] = 'in_process'
                            user_session.save_user_info()
                            send_message('Введите новый пароль', cur_chat)
                        else:
                            send_message('Неверный текущий пароль.Попробуйте снова', cur_chat)
                            user_session.save_user_info()
                    elif user_session.user_info['changer']['new_password'] == 'in_process':
                        #check password it is not common
                        old_password = user_session.user_info['changer']['old_password']
                        user_session.save_user_info()
                        if change_password(user_session.user_info['login_credentials']['username'],old_password,cur_message):
                            send_message('Пароль был изменен', cur_chat)
                            user_session.user_info['login_credentials']['password'] = cur_message
                            user_session.user_info['changer']['new_password'] = cur_message
                            user_session.update_state_user('change_password',False)
                        else:
                            send_message('Сервер недоступен.Попробуйте позже', cur_chat)
                            user_session.save_user_info()
                        ######time for delete messages################################################
                    elif cur_message == 'сменить время чистки':
                        send_message('Введите желаемое время чистки в секундах:', cur_chat)
                        send_message('в данный момент значение равно {} секунд'.format(user_session.user_info['time_for_check_updates']), cur_chat) 
                        user_session.update_state_user('change_time_check_updates','in_process')
                        user_session.save_user_info()
                    elif user_session.user_info['state']['change_time_check_updates'] == 'in_process':
                        if not (cur_message.isnumeric()):
                            send_message('введите цифры', cur_chat)
                        else:
                            if int(cur_message) < 60:
                                send_message('введите значение большее 60', cur_chat)
                                user_session.save_user_info()
                            else:
                                send_message('Значение зафиксировано', cur_chat, login_keyboard)
                                user_session.user_info['time_for_check_updates'] = cur_message
                                user_session.update_state_user('change_time_check_updates',False)
                                user_session.save_user_info()
                                change_delete_time(user_session.user_info['login_credentials']['username'],user_session.user_info['login_credentials']['password'],cur_message)
                                
                ################menu without login###################################################
                else:
    #################selectors################################################################    
                    if cur_message:
                        if user_session.user_info['state']['created'] == 'in_process' or  user_session.user_info['state']['login'] == 'in_process' or cur_message =='регистрация' or cur_message == 'войти':
                            send_raw_message('👌', cur_chat, kick_out)
                        else:
                            send_message('выберите вариант', cur_chat, menu_keyboard)
                    if cur_message == 'регистрация':
                            send_message('Придумайте и введите логин на английском', cur_chat)
                            user_session.update_state_user('created','in_process')
                            user_session.update_user_creditails('profile','username','in_process')
                    elif cur_message == 'назад':
                        hide_tracks(user_session)
                        user_session.clean_session()
                        send_message('выберите вариант', cur_chat, menu_keyboard)
                    elif cur_message == 'войти':
                            send_message('Введите ваш логин', cur_chat)
                            user_session.update_state_user('login','in_process')
                            user_session.update_user_creditails('login_credentials','username','in_process')
    ##################inside login##########################################################################
                    elif user_session.user_info['state']['login'] == 'in_process':
                        if user_session.user_info['login_credentials']['username'] == 'in_process':
                            exist = user_exist(cur_message)
                            if not exist:
                                send_message('Пользователь с таким логином не существует проверьте правильность вашего логина', cur_chat)
                            else:
                                user_session.update_user_creditails('login_credentials','username',cur_message)
                                user_session.update_user_creditails('login_credentials','password','in_process')
                                send_message('Введите ваш пароль', cur_chat)
                        elif user_session.user_info['login_credentials']['password'] == 'in_process':
                            login = do_login(user_session.user_info['login_credentials']['username'],cur_message,True)
                            if login:
                                send_message('Вы авторизованы в системе', cur_chat)
                                user_session.save_user_info()
                                user_session.update_user_creditails('login_credentials','password',cur_message)
                                user_session.user_info['time_for_check_updates'] = login['time_for_clear_messages']
                                user_session.update_state_user('login',True,cur_message)
                                user_session.save_user_info()
                                send_message('Выбирете вариант', cur_chat, login_keyboard)
                            else:
                                send_message('Неправильный пароль,введите пароль еще раз', cur_chat)
    ##################inside register##########################################################################
                    elif user_session.user_info['state']['created'] == 'in_process':
                        if user_session.user_info['profile']['username'] == 'in_process':
                                exist = user_exist(cur_message)
                                if exist:
                                    send_message('Пользователь с таким логином уже существует придумайте другое имя', cur_chat)
                                else:
                                    user_session.update_user_creditails('profile','username',cur_message)
                                    send_message('Имя свободно', cur_chat)
                                    send_message('Придумайте пароль не менее 8 символов, пароль не должен быть простым', cur_chat)
                                    user_session.update_user_creditails('profile','password1','in_process')
                        elif user_session.user_info['profile']['password1'] == 'in_process':
                            if re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', cur_message):
                                send_message('Подтвердите пароль', cur_chat)
                                user_session.update_user_creditails('profile','password1',cur_message)
                                user_session.update_user_creditails('profile','password2','in_process')
                            else:
                                send_message('пароль либо слишком прост,либо не меньше 8 символов', cur_chat)
                        elif user_session.user_info['profile']['password2'] == 'in_process':
                            if re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', cur_message) and user_session.user_info['profile']['password1'] == cur_message:
                                send_message('Пароли совпадают', cur_chat)
                                user_session.update_user_creditails('profile','password2',cur_message)
                                user_session.update_state_user('created',True,cur_message)
                                success = create_user(user_session.user_info['profile']['username'],user_session.user_info['profile']['password2'])
                                user_session.save_user_info()
                                if success:
                                    send_message('Вы успешно зарегистрированы.Что бы начать пользоваться ботом авторизуйтесь.', cur_chat)
                                    send_message('Запомните или запишите свой логин и пароль так как востановить его будет невозможно', cur_chat)
                                    send_message('Ваш логин {}.Ваш пароль {}'.format(user_session.user_info['profile']['username'],user_session.user_info['profile']['password2']), cur_chat)
                                    user_session.update_state_user('created',True,user_session.user_info['profile']['password2'])
                                    user_session.save_user_info()
                                    send_message('выберите вариант', cur_chat, menu_keyboard)
                                else:
                                    send_message('Что то не так с сервером попробуйте позже'.format(cur_user), cur_chat)
                                    user_session.save_user_info()
                            else:
                                send_message('Пароли не совпадают', cur_chat)
                                send_message('Попробуйте еще раз ', cur_chat)
                time.sleep(0.5)
def main_flow():
    check_telegram_updates()
    

if __name__ == '__main__':
    if len(sys.argv) >1:
        if sys.argv[1] == '--debug':
            do_some_protection()
            main_flow()
    else:
        main_flow()
    



