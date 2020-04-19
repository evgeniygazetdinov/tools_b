def create_new_user_handler(username,password):
    pass


def login_handler(username,password):
    pass


def password_handler(username):
    send_message('hello {} you not registed. please type your password look like "my_password=YOUR PASSWORD"'.format(cur_user), cur_chat) 
    return password