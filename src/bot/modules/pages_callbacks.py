import telebot
from ..core.pages import Pages, messages_pages, Keyboard_pages
from ..core.logs import logger

def setup_pages_cb_module(bot: telebot.TeleBot):
    @bot.callback_query_handler(func= lambda call: call.data in ["turn_left", "turn_right"])
    def turn_pages(call: telebot.types.CallbackQuery):
        tmp = messages_pages.get(call.from_user.id)

        if tmp == None:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        page_obj = tmp.get(call.message.message_id)
        if type(page_obj) == Pages:
            if page_obj == None:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                return
                    
            if call.data == "turn_right":
                turn_page = page_obj.turn_right_page()

            elif call.data == "turn_left":
                turn_page = page_obj.turn_left_page()

            if turn_page == call.message.text or turn_page == False:
                return

            try:
                bot.edit_message_text(turn_page,
                                    call.message.chat.id,
                                    call.message.id,
                                    reply_markup=call.message.reply_markup,
                                    parse_mode="HTML",
                                    disable_web_page_preview=True)
            except telebot.apihelper.ApiTelegramException:
                logger.warning(f"Пользователь ({call.from_user.username}:{call.from_user.id}): ошибка перевертыш")
                turn_pages(call=call)
                
        elif type(page_obj) == Keyboard_pages:
            if page_obj == None:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                return
                    
            if call.data == "turn_right":
                turn_page = page_obj.turn_right_page()

            elif call.data == "turn_left":
                turn_page = page_obj.turn_left_page()

            if turn_page == call.message.text or turn_page == False:
                return

            bot.edit_message_text(call.message.text,
                                call.message.chat.id,
                                call.message.id,
                                reply_markup=turn_page,
                                parse_mode="HTML",
                                disable_web_page_preview=True)