

def accept_ok():
     return user_session.user_info["state"]["upload"] == "in_process"
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
                        or cur_message == "сменить время чистки" )