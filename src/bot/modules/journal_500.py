import telebot
from ...api.Journal_API import API
from ..core.storage import db_obj, user_auths

def setup_error_module(Bot: telebot.TeleBot):
    global bot
    bot = Bot

def check_server_error(func):
    def wrapper(message_or_call):
        print(123)
        User_dict: dict = user_auths.get(message_or_call.from_user.id)
        User: API = User_dict.get("User_obj")
        status = User.check_server_work()

        if status == False:
            print(1)
            bot.send_message(message_or_call.chat.id, "❗️Основной функционал бота недоступен из-за проблем со стороны основного журнала, попробуйте позже")
            return
        else:
            print(2)
            return message_or_call
        
    return wrapper