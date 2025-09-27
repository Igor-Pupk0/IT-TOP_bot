from .authorization import check_auth
from .start import generate_start_message
import telebot

def setup_returns_module(bot: telebot.TeleBot):
    @bot.callback_query_handler(func= lambda call: "return" in call.data)
    @check_auth
    def menu_return(call: telebot.types.CallbackQuery):
        if call.data == "return_main":
            text, keyboard = generate_start_message()
            bot.edit_message_text(text, call.message.chat.id,
                                  call.message.message_id,
                                  parse_mode="HTML")
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)