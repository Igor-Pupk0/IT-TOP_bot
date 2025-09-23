###
### Тут реализована авторизация и проверка на нее
###

from functools import wraps
from telebot import types
from src.api.Journal_API import API
from .storage import db_obj, users_states, user_auths

def check_auth(func):
    @wraps(func)
    def wrapper(message_or_call):
        user_data = db_obj.get_all_by_telegram_id(message_or_call.from_user.id)
        user_states = users_states.get(message_or_call.from_user.id)

        if user_auths.get(message_or_call.from_user.id) is None and user_data is not None:
            user_auths[message_or_call.from_user.id] = {
                "username": user_data[0],
                "password": user_data[1],
                "User_obj": API(user_data[0], user_data[1], user_data[2])
            }

        if user_data is None and user_states.auth_status == "No_auth":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Авторизоваться", callback_data="auth"))
            message_or_call.bot.send_message(message_or_call.chat.id, "Авторизируйтесь!", reply_markup=markup)
            return

        if user_data and user_data[2] == 'None':
            db_obj.update_user_JWT_token(user_data[0], user_auths[message_or_call.from_user.id]["User_obj"].JWT_TOKEN)

        return func(message_or_call)
    return wrapper