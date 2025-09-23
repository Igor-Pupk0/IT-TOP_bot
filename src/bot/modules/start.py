from telebot import types

def setup_start_module(bot):
    @bot.message_handler(commands=['start'])
    def start(message):
        keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        keyboard.add(
            types.KeyboardButton("📅 Посмотреть раписание"),
            types.KeyboardButton("🕵🏿‍♂️ Профиль"),
            types.KeyboardButton("📔 Посмотреть ДЗ")
        )
        bot.send_message(message.chat.id, 
            "Это Айте топ бот, тут можно смотреть расписание и не только. Бот еще в разработке", 
            reply_markup=keyboard)
        

