from .authorization import check_auth
import telebot

def setup_returns_module(bot):
    @bot.callback_query_handler(func= lambda call: "return" in call.data)
    @check_auth
    def menu_return(call):
        if call.data == "return_main":
            keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            keyboard.add(
                telebot.types.KeyboardButton("📅 Посмотреть раписание"),
                telebot.types.KeyboardButton("🕵🏿‍♂️ Профиль"),
                telebot.types.KeyboardButton("📔 Посмотреть ДЗ")
            )
            bot.send_message(call.message.chat.id, 
                "Это Айте топ бот, тут можно смотреть расписание и не только. Бот еще в разработке", 
                reply_markup=keyboard)
        bot.delete_message(call.message.chat.id, call.message.message_id)