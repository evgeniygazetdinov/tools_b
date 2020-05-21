import os
import requests
import time
import urllib
import re
import sys
import datetime
import threading
from multiprocessing import Process,current_process,cpu_count,active_children
from lib.sessions import Session
from lib.session_methods import check_user_actions,send_raw_message, hide_tracks
from lib.const import  URL, menu_items, login_items, kick_out
from lib.protect import do_some_protection
from lib.active_users import get_active_users, save_users_state, push_active_users, remove_active_users
from lib.backend_methods import change_password, user_exist, create_user, upload_photo_from_telegram_and_get_path,do_login, upload_photo_on_server
from lib.base import  (clean_patern, send_message, get_url, find_user_message_chat,
                  div_password, build_keyboard, get_json_from_url,get_last_update_id,
                  get_updates, get_updates, get_last_chat_id_and_text, telegram_clean_history)


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
                print(user_session.__dict__)
                if cur_message:
                    #remove active threads before
                    #here save user_message_info session
                    active_users = get_active_users()
                    for p in active_children():
                       
                        if p.name in active_users['users']:
                             if p.name == cur_user:
                                p.terminate()
                                remove_active_users(cur_user)
                        else:
                            continue
                    user_session.update_user_info('pushed_button',True)
                    #BEGIN new counter user action
                    thread2 = Process(name ="{}".format(cur_user),target=check_user_actions,args = (cur_user, user_session))
                    thread2.start()
                #message-handlers
                if cur_message == '/start':
                    send_message("hello this photohosting bot please create profile or login",cur_chat)
                    send_message('Choose your variant', cur_chat, menu_keyboard)
                if user_session.user_info['state']['login'] and user_session.user_info['password']:
                    send_message('Choose your variant', cur_chat, login_keyboard)
                ###############end_session##################################################
                    if cur_message =='end_sessions' and  user_session.user_info['state']['login']:
                        user_session.clean_session()
                        send_message('Session was cleaned ', cur_chat)
                        send_message('goodbye', cur_chat)
                        send_message('Choose your variant', cur_chat, menu_keyboard)
                #############upload_image###############################################
                    if cur_message =='upload_image':
                        send_message('Drag your image', cur_chat)
                        user_session.update_state_user('upload','in_process')

                    if re.match(r'download_link=', cur_message) and user_session.user_info['state']['upload'] == 'in_process':
                        url = clean_patern(cur_message)
                        filename,path_file = upload_photo_from_telegram_and_get_path(url)
                        sucess_upload = upload_photo_on_server(filename,cur_user,user_session.get_user_info_value('password'))
                        os.remove(path_file)
                        user_session.save_user_info()
                        if sucess_upload:
                            send_message('file uploaded', cur_chat)
                            user_session.save_user_info()
                        else:
                            send_message('something bad with server.Try again later'.format(cur_user), cur_chat)
                            user_session.save_user_info()
                        send_message('Choose your variant', cur_chat, login_keyboard)
                        user_session.save_user_info()
                ###########my_uploads#########################################
                    if re.match('my_uploads',cur_message) and user_session.user_info['state']['login'] and user_session.get_user_info_value('password'):
                        content = do_login(cur_user,user_session.get_user_info_value('password'),cur_chat,show_user_content=True)
                        user_session.save_user_info()
                        if content:
                            if len(content['photos']) > 0:
                                for photo in content['photos']:
                                    send_message("""
                                                    id: {} 
                                                    \n created: {} 
                                                    \n unique link:
                                                        {} 
                                                    \n delete link:
                                                        {} 
                                                    \n views:
                                                        {}
                                                    \n """.format(photo['id'],photo['created_date'],photo['unique_link'],photo['delete_by_unique_link'],[view for view in photo['views']]), cur_chat)
                                print(photo['unique_link'])
                                user_session.save_user_info()
                            else:
                                send_message('no photos', cur_chat)
                                user_session.save_user_info()
                ##########change password######################################
                    if re.match('change_password',cur_message) and user_session.user_info['state']['login'] and user_session.user_info['password']:
                        send_message('put your old password', cur_chat)
                        send_message('oldpassword= YOUR OLD PASSWORD', cur_chat)
                        user_session.update_state_user('change_password','in_process')
                    if re.match(r'oldpassword=', cur_message) and user_session.user_info['state']['change_password'] == 'in_process':
                        old_password = clean_patern(cur_message)
                        if old_password == user_session.get_user_info_value('password'):
                            user_session.user_info['changer']['old_password'] = old_password
                            user_session.save_user_info()
                            send_message('put new_password', cur_chat)
                            send_message('newpassword=YOUR NEW PASSWORD', cur_chat)
                        else:
                            send_message('this not look like your current password', cur_chat)
                            user_session.save_user_info()

                    if re.match(r'newpassword=', cur_message) and user_session.user_info['state']['change_password'] == 'in_process':
                        new_password = clean_patern(cur_message)
                        #check password it is not common
                        old_password = user_session.user_info['changer']['old_password']
                        user_session.save_user_info()
                        if change_password(cur_user,old_password,new_password):
                            send_message('password was changed', cur_chat)
                            user_session.user_info['password'] = new_password
                            user_session.user_info['changer']['new_password'] = new_password
                            user_session.update_state_user('change_password',True)
                        else:
                            send_message('something bad with server try again later', cur_chat)
                            user_session.save_user_info()
                ################menu without login###################################################
                else:
                    if cur_message:
                        if user_session.user_info['state']['created'] == 'in_process' or cur_message =='регистрация':
                            send_raw_message('выберите вариант', cur_chat, kick_out)
                        else:
                            send_message('выберите вариант', cur_chat, menu_keyboard)
                    if cur_message == 'регистрация':
                            send_message('Придумайте и введите логин на английском', cur_chat)
                            user_session.update_state_user('created','in_process')
                            user_session.update_user_creditails('profile','username','in_process')
                    elif cur_message == 'выйти':
                        hide_tracks(user_session)
                        user_session.clean_session()
                        send_message('выберите вариант', cur_chat, menu_keyboard)
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
    



