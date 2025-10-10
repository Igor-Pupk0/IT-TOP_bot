from .authorization import check_auth
from .start import generate_start_message
import telebot
from .homework.send_homework import homework_pages_data
from ..core.states import get_user_status

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
        
        match call.data:
            case "return_homework":
                if homework_pages_data.get(call.from_user.id) != None:
                    homework_pages_data.pop(call.from_user.id)

            case "return_and_delete_homework":
                if homework_pages_data.get(call.from_user.id) != None:
                    homework_pages_data.pop(call.from_user.id)
                bot.delete_message(call.message.chat.id, call.message.id)
                
            case "return_broadcast":
                get_user_status(call.from_user.id).broadcast_typing_status = False
                bot.delete_message(call.message.chat.id, call.message.id)
            
        bot.delete_message(call.message.chat.id, call.message.message_id)