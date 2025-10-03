###
### Тут реализована авторизация и проверка на нее
###

from functools import wraps
import telebot
from src.api.Journal_API import API
from ..core.storage import db_obj, user_auths
from ..core.states import get_user_status
from ..core.logs import logger

def setup_auth_module(Bot: telebot.TeleBot):
    global bot
    bot = Bot

    ### Инициализация авторизации
    @bot.callback_query_handler(func= lambda call: call.data == "auth" )
    def user_auth(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) инициализировал процесс авторизации")
        user_data = db_obj.get_all_by_telegram_id(call.from_user.id)

        if user_data != None:
            bot.send_message(call.message.chat.id, "Ты уже авторизован!")
            return
        get_user_status(call.from_user.id).auth_status = "Auth_on_username"
        bot.send_message(call.message.chat.id, "Логин:")

    ### Авторизация
    @bot.message_handler(func=lambda message: get_user_status(message.from_user.id).auth_status == "Auth_on_username")
    def auth_username(message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел логин")
        username = message.text
        user_states = get_user_status(message.from_user.id)
        user_states.auth_status = "No_auth"
        user_states.auth_status = "Auth_on_password"
        bot.send_message(message.chat.id, "Пароль:")
        user_auths[message.from_user.id] = {"username": username, "password": None}

    @bot.message_handler(func=lambda message: get_user_status(message.from_user.id).auth_status == "Auth_on_password")
    def auth_password(message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел пароль")
        password = message.text
        user_states = get_user_status(message.from_user.id)
        user_states.auth_status = "No_auth"
        user_auths[message.from_user.id]["password"] = password
        bot.send_message(message.chat.id, "Вхожу...")
        user_auths[message.from_user.id]["User_obj"] = API(user_auths[message.from_user.id]["username"], user_auths[message.from_user.id]["password"])
        
        if user_auths[message.from_user.id]["User_obj"].succesful_auth == False:
            logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел неправильные данные для входа")
            bot.send_message(message.chat.id, "Неправильные данные")
            user_auths.pop(message.from_user.id)
        else:
            logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) вошел в аккаунт")
            bot.send_message(message.chat.id, "Успешный вход!")
            db_obj.insert_user_creds(message.from_user.id, user_auths[message.from_user.id]["username"], user_auths[message.from_user.id]["password"])
            db_obj.update_user_JWT_token(user_auths[message.from_user.id]["username"], user_auths[message.from_user.id]["User_obj"].JWT_TOKEN)


    @bot.callback_query_handler(func= lambda call: call.data == "logout" )
    @check_auth
    def logout(call):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) вышел из аккаунта")
        db_obj.delete_user_by_telegram_id(call.from_user.id)
        if user_auths.get(call.message.from_user.id) != None:
            user_auths.pop(call.message.from_user.id)
        bot.send_message(call.message.chat.id, "Вы успешно вышли из аккаунта ✅")


def check_auth(func):
    @wraps(func)
    def wrapper(message_or_call):
        user_data = db_obj.get_all_by_telegram_id(message_or_call.from_user.id)
        user_states = get_user_status(message_or_call.from_user.id)


        if user_auths.get(message_or_call.from_user.id) is None and user_data is not None:
            user_auths[message_or_call.from_user.id] = {
                "username": user_data[0],
                "password": user_data[1],
                "User_obj": API(user_data[0], user_data[1], user_data[2])
            }

        if user_data is None and user_states.auth_status == "No_auth":
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("Авторизоваться", callback_data="auth"))
            bot.send_message(message_or_call.chat.id, "Авторизируйтесь!", reply_markup=markup)
            return

        if user_data and user_data[2] == 'None':
            db_obj.update_user_JWT_token(user_data[0], user_auths[message_or_call.from_user.id]["User_obj"].JWT_TOKEN)

        return func(message_or_call)
    return wrapper

