import telebot
from src.bot.core.logs import logger
from ..core.storage import SUPPORT_USERNAME

def setup_start_module(bot: telebot.TeleBot):
    @bot.message_handler(commands=['start'])
    def start(message: telebot.types.Message):
        if message.from_user.id == bot.bot_id:
            pass
        else:
            logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел команду /start")

        text, keyboard = generate_start_message()

        bot.send_message(message.chat.id, 
            text, 
            reply_markup=keyboard,
            parse_mode="HTML")
            
    return start

def generate_start_message() -> str:
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add(
        telebot.types.KeyboardButton("📅 Раписание"),
        telebot.types.KeyboardButton("🕵🏿‍♂️ Профиль"),
        telebot.types.KeyboardButton("📔 ДЗ"),
        telebot.types.KeyboardButton("5️⃣ Оценки"),
        telebot.types.KeyboardButton("🐥 Разное")
    )
    text = f"Это бот-журнал или журнл в обертке тг бота\nБот еще в разработке, связь с разработчиком: <a href='t.me/{SUPPORT_USERNAME}'>Кликабельно</a>"
    return (text, keyboard)