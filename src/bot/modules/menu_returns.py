from .authorization import check_auth
import telebot

def setup_returns_module(bot, start_func):
    @bot.callback_query_handler(func= lambda call: "return" in call.data)
    @check_auth
    def menu_return(call: telebot.types.CallbackQuery):
        if call.data == "return_main":
            start_func(call.message)
        bot.delete_message(call.message.chat.id, call.message.message_id)