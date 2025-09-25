import telebot
from src.bot.core.pages import Pages, messages_pages

def setup_pages_cb_module(bot: telebot.TeleBot):
    @bot.callback_query_handler(func= lambda call: call.data in ["turn_left", "turn_right"])
    def turn_pages(call: telebot.types.CallbackQuery):
        page_obj: Pages = messages_pages.get(call.message.message_id)
        
        if page_obj == None:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return
                
        if call.data == "turn_right":
            right_page = page_obj.turn_right_page()

            if right_page == call.message.text:
                return
            bot.edit_message_text(right_page,
                                  call.message.chat.id,
                                  call.message.id,
                                  reply_markup=call.message.reply_markup,
                                  parse_mode="HTML",
                                  disable_web_page_preview=True)
            
        elif call.data == "turn_left":
            left_page = page_obj.turn_left_page()

            if left_page == call.message.text:
                return

            bot.edit_message_text(left_page, 
                                  call.message.chat.id, 
                                  call.message.id, 
                                  reply_markup=call.message.reply_markup, 
                                  parse_mode="HTML",
                                  disable_web_page_preview=True)