import telebot
from ...api.Journal_API import API
from ..core.storage import db_obj, user_auths
from ..core.logs import logger

def setup_error_module(Bot: telebot.TeleBot):
    global bot
    bot = Bot

def check_server_error(func):
    def wrapper(message_or_call):
        User_dict: dict = user_auths.get(message_or_call.from_user.id)
        User: API = User_dict.get("User_obj")
        status = User.check_server_work()

        if status == False:
            bot.send_message(message_or_call.chat.id, "❗️Основной функционал бота недоступен из-за проблем со стороны основного журнала, попробуйте позже")
            logger.warning(f"Пользователь ({message_or_call.from_user.username}:{message_or_call.from_user.id}): Журнал не работает")
            return
        else:
            return func(message_or_call)
        
    return wrapper