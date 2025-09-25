import telebot
from src.bot.core.logs import logger

def setup_start_module(bot):
    @bot.message_handler(commands=['start'])
    def start(message: telebot.types.Message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел команду /start")
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        keyboard.add(
            telebot.types.KeyboardButton("📅 Посмотреть раписание"),
            telebot.types.KeyboardButton("🕵🏿‍♂️ Профиль"),
            telebot.types.KeyboardButton("📔 Посмотреть ДЗ")
        )
        bot.send_message(message.chat.id, 
            "Это Айте топ бот, тут можно смотреть расписание и не только. Бот еще в разработке", 
            reply_markup=keyboard)
        

