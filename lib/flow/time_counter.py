from multiprocessing import active_children, Process

from lib.active_users import get_active_users, remove_active_users
from lib.session_methods import check_user_actions


def time_handler(cur_user, user_session):
    # remove active threads before
    # here save user_message_info session
    active_users = get_active_users()
    for p in active_children():
        if int(p.name) in active_users["users"]:
            if int(p.name) == cur_user:
                p.terminate()
                remove_active_users(cur_user)
        else:
            continue
    user_session.update_user_info("pushed_button", True)
    # BEGIN new counter user action
    thread2 = Process(
        name="{}".format(cur_user),
        target=check_user_actions,
        args=(cur_user, user_session),
    )
    thread2.start()