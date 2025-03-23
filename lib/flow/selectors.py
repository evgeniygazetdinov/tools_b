import re

from lib.backend_methods import user_exist, do_login, create_user
from lib.base import send_message
from lib.buttons import kick_out
from lib.session_methods import send_raw_message, hide_tracks


def selectors(cur_message, cur_chat, user_session, menu_keyboard, login_keyboard, cur_user):
    user_info = user_session.get('user_info', {})
    user_state =  user_session.user_info.get("state", {})
    login_state = user_state.get("login")
    login_cred  = user_info.get("login_credentials",{})
    if cur_message:
        if (
                user_session.user_info["state"]["created"] == "in_process"
                or user_session.user_info["state"]["login"] == "in_process"
                or cur_message == "регистрация"
                or cur_message == "войти"
        ):
            send_raw_message("👌", cur_chat, kick_out)
        else:
            send_message("выберите вариант", cur_chat, menu_keyboard)
    if cur_message == "регистрация":
        send_message("Придумайте и введите логин на английском", cur_chat)
        user_session.update_state_user("created", "in_process")
        user_session.update_user_creditails(
            "profile", "username", "in_process"
        )
    elif cur_message == "назад":
        hide_tracks(user_session)
        user_session.clean_session()
        send_message("выберите вариант", cur_chat, menu_keyboard)
    elif cur_message == "войти":
        send_message("Введите ваш логин", cur_chat)
        user_session.update_state_user("login", "in_process")
        user_session.update_user_creditails(
            "login_credentials", "username", "in_process"
        )
        ##################inside login##########################################################################
    elif login_state == "in_process":
        if login_cred.get("username")== "in_process":
            exist = user_exist(cur_message)
            if not exist:
                send_message(
                    "Пользователь с таким логином не существует проверьте правильность вашего логина",
                    cur_chat,
                )
            else:
                user_session.update_user_creditails(
                    "login_credentials", "username", cur_message
                )
                user_session.update_user_creditails(
                    "login_credentials", "password", "in_process"
                )
                send_message("Введите ваш пароль", cur_chat)
        elif (
                user_session.user_info["login_credentials"]["password"]
                == "in_process"
        ):
            login = do_login(
                user_session.user_info["login_credentials"]["username"],
                cur_message,
                True,
            )
            if login:
                send_message("Вы авторизованы в системе", cur_chat)
                user_session.save_user_info()
                user_session.update_user_creditails(
                    "login_credentials", "password", cur_message
                )
                user_session.user_info["time_for_check_updates"] = login[
                    "time_for_clear_messages"
                ]
                user_session.update_state_user("login", True, cur_message)
                user_session.save_user_info()
                send_message("Выбирете вариант", cur_chat, login_keyboard)
            else:
                send_message(
                    "Неправильный пароль,введите пароль еще раз", cur_chat
                )
        ##################inside register##########################################################################
    elif user_state.get("created") == "in_process":
        if user_session.user_info["profile"]["username"] == "in_process":
            exist = user_exist(cur_message)
            if exist:
                send_message(
                    "Пользователь с таким логином уже существует придумайте другое имя",
                    cur_chat,
                )
            else:
                user_session.update_user_creditails(
                    "profile", "username", cur_message
                )
                send_message("Имя свободно", cur_chat)
                send_message(
                    "Придумайте пароль не менее 8 символов, пароль не должен быть простым",
                    cur_chat,
                )
                user_session.update_user_creditails(
                    "profile", "password1", "in_process"
                )
        elif user_session.user_info["profile"]["password1"] == "in_process":
            if re.match(r"[A-Za-z0-9@#$%^&+=]{8,}", cur_message):
                send_message("Подтвердите пароль", cur_chat)
                user_session.update_user_creditails(
                    "profile", "password1", cur_message
                )
                user_session.update_user_creditails(
                    "profile", "password2", "in_process"
                )
            else:
                send_message(
                    "пароль либо слишком прост,либо не меньше 8 символов",
                    cur_chat,
                )
        elif user_session.user_info["profile"]["password2"] == "in_process":
            if (
                    re.match(r"[A-Za-z0-9@#$%^&+=]{8,}", cur_message)
                    and user_session.user_info["profile"]["password1"]
                    == cur_message
            ):
                send_message("Пароли совпадают", cur_chat)
                user_session.update_user_creditails(
                    "profile", "password2", cur_message
                )
                user_session.update_state_user("created", True, cur_message)
                success = create_user(
                    user_session.user_info["profile"]["username"],
                    user_session.user_info["profile"]["password2"],
                )
                user_session.save_user_info()
                if success:
                    send_message(
                        "Вы успешно зарегистрированы.Что бы начать пользоваться ботом авторизуйтесь.",
                        cur_chat,
                    )
                    send_message(
                        "Запомните или запишите свой логин и пароль так как востановить его будет невозможно",
                        cur_chat,
                    )
                    send_message(
                        "Ваш логин {}.Ваш пароль {}".format(
                            user_session.user_info["profile"]["username"],
                            user_session.user_info["profile"]["password2"],
                        ),
                        cur_chat,
                    )
                    user_session.update_state_user(
                        "created",
                        True,
                        user_session.user_info["profile"]["password2"],
                    )
                    user_session.save_user_info()
                    send_message(
                        "выберите вариант", cur_chat, menu_keyboard
                    )
                else:
                    send_message(
                        "Что то не так с сервером попробуйте позже".format(
                            cur_user
                        ),
                        cur_chat,
                    )
                    user_session.save_user_info()
            else:
                send_message("Пароли не совпадают", cur_chat)
                send_message("Попробуйте еще раз ", cur_chat)