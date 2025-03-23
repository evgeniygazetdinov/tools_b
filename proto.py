# -*- coding: utf-8 -*-
import sys
import asyncio

from lib.flow.selectors import selectors

print(sys.getdefaultencoding())
import json
import os
import re
import sys

from multiprocessing import Process, active_children
from lib.photo_display_methods import (
    get_uploaded_photos_from_response,
    get_newest_upload_list,
    delete_viewed_photos,
    clean_empty_uploadlists,
)

from lib.sessions import Session
from lib.session_methods import check_user_actions, send_raw_message, hide_tracks
from lib.buttons import (
    menu_items,
    login_items,
    kick_out,
    under_upload_menu,
)
from lib.active_users import (
    push_active_users,
)
from lib.backend_methods import (
    change_password,
    upload_photo_from_telegram_and_get_path,
    do_login,
    upload_photo_on_server,
    change_delete_time,
    change_photoposition,
    change_description,
    add_photos_to_upload_list,
)
from lib.base import (
    clean_patern,
    send_message,
    find_user_message_chat,
    build_keyboard,
    get_last_update_id,
    get_updates,
    make_filestring_for_request,
)
from lib.flow.time_counter import time_handler

async def check_telegram_updates():
    last_update_id = None
    cur_message = None
    user_session = {}
    cur_chat = None
    menu_keyboard = None
    login_keyboard = None
    cur_user = None
    while True:
        try:
            # Создаем и ждем выполнения задачи получения обновлений
            updates = await get_updates(last_update_id)
            
            if len(updates["result"]) > 0:
                # Обработка обновлений
                last_update_id = get_last_update_id(updates) + 1
                cur_user, cur_chat, cur_message, message_id = find_user_message_chat(
                    updates["result"]
                )
                push_active_users(cur_user)
                login_keyboard = build_keyboard(login_items)
                menu_keyboard = build_keyboard(menu_items)
                user_session = Session(cur_user, cur_chat, message_id)
                if cur_message == "/start":
                    send_message("Привет это бот фотохостинга", cur_chat)
                if cur_message:
                   time_handler(cur_message, user_session)
                if user_session.user_info["state"]["login"] == True:
                    if (
                        user_session.user_info["state"]["upload"] == "in_process"
                        or user_session.user_info["state"]["change_password"]
                        == "in_process"
                        or user_session.user_info["state"]["change_time_check_updates"]
                        == "in_process"
                        or user_session.user_info["state"]["upload"]
                        or user_session.user_info["photo_position"]["longitude"]
                        or user_session.user_info["photo_position"]["latitude"]
                        or cur_message == "загрузить фото"
                        or cur_message == "инструкции"
                        or cur_message == "сменить пароль"
                        or cur_message == "сменить время чистки"
                    ):
                        send_raw_message("👌", cur_chat, kick_out)
                    elif (
                        cur_message == "мои загрузки"
                        or user_session.user_info["on_check_photos"]
                    ):
                        send_message("👌", cur_chat, under_upload_menu)
                    else:
                        send_message("выберите вариант", cur_chat, login_keyboard)
                    if cur_message == "назад" and user_session.user_info["on_check_photos"]:
                        # inside myuploads
                        user_session.user_info["on_check_photos"] = False
                        user_session.save_user_info()

                    if cur_message == "назад":
                        user_session.reset_login_session()
                        send_message("выберите вариант", cur_chat, login_keyboard)

                    ###############end_session##################################################
                    if cur_message == "завершить сессию":
                        send_message("Досвидания", cur_chat)
                        hide_tracks(user_session)
                        user_session.clean_session()
                    #############upload_image###############################################
                    if cur_message == "загрузить фото":
                        send_message("Перетяните или выберете изоображение", cur_chat)
                        user_session.update_state_user("upload", "in_process")
                    if (
                        re.match(r"download_link=", cur_message)
                        and user_session.user_info["state"]["upload"] == "in_process"
                    ):
                        url = clean_patern(cur_message)
                        filename, path_file = upload_photo_from_telegram_and_get_path(url)
                        sucess_upload = upload_photo_on_server(
                            filename,
                            user_session.user_info["login_credentials"]["username"],
                            user_session.user_info["login_credentials"]["password"],
                            True,
                        )
                        os.remove(path_file)
                        user_session.save_user_info()
                        if sucess_upload:
                            send_message("Добавьте геопозицию к фото", cur_chat)
                            filename = (str(sucess_upload["image"]).split("/media/"))[-1]
                            if isinstance(filename, str):

                                user_session.user_info["uploaded_photos"].append(filename)
                                user_session.user_info["photo_position"][
                                    "filename"
                                ] = filename
                                user_session.update_state_user("upload", "on_geoposition")

                    elif (
                        re.match(r"location=", cur_message)
                        and user_session.user_info["state"]["upload"] == "on_geoposition"
                    ):
                        # remove 'location=' from str and converting to dict
                        location_str = (clean_patern(cur_message)).replace("'", '"')
                        location = json.loads(location_str)
                        position = change_photoposition(
                            user_session.user_info["login_credentials"]["username"],
                            user_session.user_info["login_credentials"]["password"],
                            user_session.user_info["photo_position"]["filename"],
                            location["longitude"],
                            location["latitude"],
                        )
                        user_session.update_state_user("upload", "on_description")
                        if position:
                            send_message("Геоданные добавлены", cur_chat)
                        else:
                            send_message("Сервер недоступен.Попробуйте позже", cur_chat)
                        send_message("Добавьте описание к фото", cur_chat)
                    elif user_session.user_info["state"]["upload"] == "on_description":
                        description = change_description(
                            user_session.user_info["login_credentials"]["username"],
                            user_session.user_info["login_credentials"]["password"],
                            user_session.user_info["photo_position"]["filename"],
                            cur_message,
                        )
                        if description:
                            send_message("Описание  добавлено", cur_chat)

                        else:
                            send_message("Сервер недоступен.Попробуйте позже", cur_chat)
                        send_message(
                            "Перетяните или выберете изоображение или нажмите назад для выхода",
                            cur_chat,
                        )
                        user_session.update_state_user("upload", "in_process")
                    elif cur_message == "назад":
                        if len(user_session.user_info["uploaded_photos"]) != 0:
                            files = make_filestring_for_request(
                                user_session.user_info["uploaded_photos"]
                            )
                            add_photos_to_upload_list(
                                user_session.user_info["login_credentials"]["username"],
                                user_session.user_info["login_credentials"]["password"],
                                files,
                                True,
                            )
                ###########my_uploads#########################################

                elif cur_message == "мои загрузки":
                    user_session.user_info["on_check_photos"] = True
                    user_session.save_user_info()
                elif cur_message == "веcь список":
                    content = do_login(
                        user_session.user_info["login_credentials"]["username"],
                        user_session.user_info["login_credentials"]["password"],
                        show_user_content=True,
                    )
                    clean_empty_uploadlists(
                        user_session.user_info["login_credentials"]["username"],
                        user_session.user_info["login_credentials"]["password"],
                        content,
                    )
                    # store content to session and clean empty upload list  for right display photo
                    values = get_uploaded_photos_from_response(content)
                    for key, value in values.items():
                        if isinstance(value, list):
                            send_message(
                                """список {}\nссылки:{}
                                \n просмотры:{}""".format(
                                    key,
                                    [val["link"] for val in value],
                                    [
                                        "отсутствуют"
                                        if len(val["views"]) == 0
                                        else val["views"]
                                        for val in value
                                    ],
                                ),
                                cur_chat,
                                under_upload_menu,
                            )
                        else:
                            send_message(
                                """список {}\nссылки:{} \n просмотры{}""".format(
                                    key,
                                    value["link"],
                                    [
                                        "отсутствуют"
                                        if len(value["views"]) == 0
                                        else value["views"]
                                    ],
                                ),
                                cur_chat,
                                under_upload_menu,
                            )
                elif cur_message == "новый список":

                    content = do_login(
                        user_session.user_info["login_credentials"]["username"],
                        user_session.user_info["login_credentials"]["password"],
                        show_user_content=True,
                    )
                    clean_empty_uploadlists(
                        user_session.user_info["login_credentials"]["username"],
                        user_session.user_info["login_credentials"]["password"],
                        content,
                    )
                    # store content to session and clean empty upload list  for right display photos
                    values = get_newest_upload_list(content)
                    for key, value in values.items():
                        if isinstance(value, list):
                            send_message(
                                """список {}\nссылки:{}
                                    \n просмотры:{}""".format(
                                    key,
                                    [val["link"] for val in value],
                                    [
                                        "отсутствуют"
                                        if len(val["views"]) == 0
                                        else val["views"]
                                        for val in value
                                    ],
                                ),
                                cur_chat,
                                under_upload_menu,
                            )
                        else:
                            send_message(
                                """список {}\nссылки:{} \n просмотры{}""".format(
                                    key, value["link"], [v for v in value["views"]]
                                ),
                                cur_chat,
                                under_upload_menu,
                            )
                elif cur_message == "удалить просмотренные":
                    content = do_login(
                        user_session.user_info["login_credentials"]["username"],
                        user_session.user_info["login_credentials"]["password"],
                        show_user_content=True,
                    )
                    clean_empty_uploadlists(
                        user_session.user_info["login_credentials"]["username"],
                        user_session.user_info["login_credentials"]["password"],
                        content,
                    )
                    # store content to session and clean empty upload list  for right display photos
                    viewed_photos = delete_viewed_photos(
                        user_session.user_info["login_credentials"]["username"],
                        user_session.user_info["login_credentials"]["password"],
                        content,
                    )
                    print("&" * 100)
                    print(viewed_photos)
                    for key, value in viewed_photos.items():
                        send_message(
                            "удалено  \n по ссылке {} \n просмотры{}".format(
                                key, [v for v in value["views"]]
                            ),
                            cur_chat,
                        )
                    if len(viewed_photos) == 0:
                        send_message("нет просмотренных фотографий", cur_chat)
                    else:
                        send_message("итого {}".format(len(viewed_photos)), cur_chat)

                    values = get_uploaded_photos_from_response(content)
                    for key, value in values.items():
                        number = range(len(value))
                        send_message(
                            """список {}\n{}""".format(key, value),
                            cur_chat,
                            under_upload_menu,
                        )
                elif cur_message == "новый список":
                    content = do_login(
                        user_session.user_info["login_credentials"]["username"],
                        user_session.user_info["login_credentials"]["password"],
                        show_user_content=True,
                    )
                    clean_empty_uploadlists(
                        user_session.user_info["login_credentials"]["username"],
                        user_session.user_info["login_credentials"]["password"],
                        content,
                    )
                    # store content to session and clean empty upload list  for right display photos
                    user_session.put_user_photos_to_session(content)
                    print(user_session.user_info["photos_from_requests"])
                    values = get_newest_upload_list(content)
                    for key, value in values.items():
                        send_message(
                            """список {}\n{}""".format(key, value),
                            cur_chat,
                            under_upload_menu,
                        )
                elif cur_message == "удалить просмотренные":
                    content = do_login(
                        user_session.user_info["login_credentials"]["username"],
                        user_session.user_info["login_credentials"]["password"],
                        show_user_content=True,
                    )
                    clean_empty_uploadlists(
                        user_session.user_info["login_credentials"]["username"],
                        user_session.user_info["login_credentials"]["password"],
                        content,
                    )
                    # store content to session and clean empty upload list  for right display photos
                    viewed_photos = delete_viewed_photos(
                        user_session.user_info["login_credentials"]["username"],
                        user_session.user_info["login_credentials"]["password"],
                        content,
                    )
                    for key, value in viewed_photos.items():
                        send_message(
                            "удалено  \n по ссылке {} \n просмотры{}".format(
                                key, value["views"]
                            ),
                            cur_chat,
                        )
                    send_message("итого {}".format(len(viewed_photos)), cur_chat)

                ##########change password######################################
                elif cur_message == "сменить пароль":
                    send_message("Введите текущий пароль", cur_chat)
                    user_session.user_info["changer"]["old_password"] = "in_process"
                    user_session.update_state_user("change_password", "in_process")
                elif user_session.user_info["changer"]["old_password"] == "in_process":
                    if (
                        cur_message
                        == user_session.user_info["login_credentials"]["password"]
                    ):
                        user_session.user_info["changer"]["old_password"] = cur_message
                        user_session.user_info["changer"]["new_password"] = "in_process"
                        user_session.save_user_info()
                        send_message("Введите новый пароль", cur_chat)
                    else:
                        send_message(
                            "Неверный текущий пароль.Попробуйте снова", cur_chat
                        )
                        user_session.save_user_info()
                elif user_session.user_info["changer"]["new_password"] == "in_process":
                    # check password it is not common
                    old_password = user_session.user_info["changer"]["old_password"]
                    user_session.save_user_info()
                    if change_password(
                        user_session.user_info["login_credentials"]["username"],
                        old_password,
                        cur_message,
                    ):
                        send_message("Пароль был изменен", cur_chat)
                        user_session.user_info["login_credentials"][
                            "password"
                        ] = cur_message
                        user_session.user_info["changer"]["new_password"] = cur_message
                        user_session.update_state_user("change_password", False)
                    else:
                        send_message("Сервер недоступен.Попробуйте позже", cur_chat)
                        user_session.save_user_info()
                    ######time for delete messages################################################
                elif cur_message == "сменить время чистки":
                    send_message("Введите желаемое время чистки в секундах:", cur_chat)
                    send_message(
                        "в данный момент значение равно {} секунд".format(
                            user_session.user_info["time_for_check_updates"]
                        ),
                        cur_chat,
                    )
                    user_session.update_state_user(
                        "change_time_check_updates", "in_process"
                    )
                    user_session.save_user_info()
                elif (
                    user_session.user_info["state"]["change_time_check_updates"]
                    == "in_process"
                ):
                    if not (cur_message.isnumeric()):
                        send_message("введите цифры", cur_chat)
                    else:
                        if int(cur_message) < 60:
                            send_message("введите значение большее 60", cur_chat)
                            user_session.save_user_info()
                        else:
                            send_message(
                                "Значение зафиксировано", cur_chat, login_keyboard
                            )
                            user_session.user_info[
                                "time_for_check_updates"
                            ] = cur_message
                            user_session.update_state_user(
                                "change_time_check_updates", False
                            )
                            user_session.save_user_info()
                            change_delete_time(
                                user_session.user_info["login_credentials"]["username"],
                                user_session.user_info["login_credentials"]["password"],
                                cur_message,
                            )

            ################menu without login###################################################
            else:
                #################selectors################################################################
                selectors(cur_message, cur_chat, user_session, menu_keyboard, login_keyboard, cur_user)
            # Добавляем небольшую паузу между запросами
            await asyncio.sleep(0.5)
            
        except asyncio.CancelledError:
            return
        except KeyboardInterrupt:
            print("Interrupted")
            sys.exit(0)
        except Exception as e:
            print(f"Ошибка при получении обновлений: {e}")
            await asyncio.sleep(5)  # Увеличенная пауза при ошибке


def main_flow():
    
    loop = asyncio.new_event_loop()
    loop.create_task(check_telegram_updates())
    loop.run_forever()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug":
            #do_some_protection()
            main_flow()
    else:
        main_flow()
