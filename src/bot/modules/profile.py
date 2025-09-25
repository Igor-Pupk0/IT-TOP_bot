import telebot
from .authorization import check_auth
from ..core.logs import logger

def setup_profile_module(Bot):
    @Bot.message_handler(func=lambda message: message.text == "🕵🏿‍♂️ Профиль")
    @check_auth
    def handle_message(message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) выбрал '{message.text}'")
        profile_keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        logout_button = telebot.types.InlineKeyboardButton("Выйти из аккаунта ❌", callback_data="logout")
        return_button =  return_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="return_main")

        profile_keyboard.add(logout_button, return_button)

        Bot.send_message(message.chat.id, "Твой профиль: бла бла бла скибиди жирни", reply_markup=profile_keyboard)