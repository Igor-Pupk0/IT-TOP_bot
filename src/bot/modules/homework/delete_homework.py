import telebot
from ...core.pages import Pages, messages_pages
from ...core.states import get_user_status

def setup_delete_homework_module(bot: telebot.TeleBot):
    @bot.callback_query_handler(func= lambda call: call.data == "delete_homework")
    def delete_homework(call: telebot.types.CallbackQuery):
        tmp = messages_pages.get(call.from_user.id)

        if tmp == None:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        page_obj: Pages = tmp.get(call.message.message_id)
        
        if page_obj == None:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return
                
        page_metadata = page_obj.get_page_metadata()
        homework_maded_id = page_metadata.get("homework_maded_id")

        get_user_status(call.from_user.id).API.delete_homework(homework_maded_id)

        bot.send_message(call.message.chat.id, "✅ ДЗ было удалено успешно")


