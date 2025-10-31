import telebot
from .authorization import check_auth
from ..core.logs import logger
from ..core.states import get_user_status, delete_user_status
from ..core.keyboards import make_return_button
from ..core.journal_500 import get_500_message
from ..core.storage import db_obj

def setup_profile_module(bot: telebot.TeleBot):
    @bot.message_handler(func=lambda message: message.text == "🕵🏿‍♂️ Профиль")
    @check_auth
    def handle_message(message: telebot.types.Message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) выбрал '{message.text}'")

        profile_keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        logout_button = telebot.types.InlineKeyboardButton("Выйти из аккаунта ❌", callback_data="logout")
        profile_keyboard.add(logout_button, make_return_button())

        
        user = get_user_status(message.from_user.id)
        user_info = user.API.get_user_info()

        if user_info == 500:
            get_500_message(message)
            return

        ### Дикое извлечение данных
        full_name = user_info["full_name"]
        name = full_name.split()[1]
        group_name = user_info["group_name"]

        topcoins = user_info["gaming_points"][0]["points"]
        topgems = user_info["gaming_points"][1]["points"]



        bot.send_message(message.chat.id,
f"""\
Твой профиль:
Ку, <b>{name}</b>
Твоя группа: {group_name}

Голда на балике:
    - <b>{topcoins}</b> Топкоинов 💸
    - <b>{topgems}</b> Топгемов  💎

""", 
                        reply_markup=profile_keyboard,
                        parse_mode="HTML")


def logout(telegram_id):
    logger.info(f"Пользователь (???:{telegram_id}) был кикнут из аккаунта")
    db_obj.delete_user_by_telegram_id(telegram_id)
    delete_user_status(telegram_id)