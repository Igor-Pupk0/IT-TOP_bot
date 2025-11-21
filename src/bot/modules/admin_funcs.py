import telebot
from ..core.storage import DEV_TELEGRAM_ID
from ..core.logs import logger
from ..core.storage import db_obj, settings_db_obj
from ..core.states import get_user_status
from ..core.keyboards import make_return_button
import time

checked_admins = []

broadcast_prefix = """⚠️Скибиди админ пишет:

"""

def setup_admin_module(Bot: telebot.TeleBot):
    global bot
    bot = Bot

    @bot.message_handler(commands=['skibidi_admin'])
    @check_on_dev
    def admin_panel(message: telebot.types.Message):

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
        broadcast_button = telebot.types.InlineKeyboardButton("📣 Broadcast", callback_data="admin_broadcast")

        keyboard.add(broadcast_button, make_return_button())

        bot.send_message(message.chat.id, "Чтооо админка???", reply_markup=keyboard)

    broadcasts()


def broadcasts():



    @bot.callback_query_handler(func= lambda call: "admin_broadcast" == call.data)
    @check_on_dev
    def get_broadcast_message(call: telebot.types.CallbackQuery):

        keyboard = telebot.types.InlineKeyboardMarkup()
        cancel_button = telebot.types.InlineKeyboardButton("❌ Отмена", callback_data="return_broadcast")
        keyboard.add(cancel_button)
        bot.send_message(call.message.chat.id, "Введи сообщение для броадкаста", reply_markup=keyboard)
        get_user_status(call.from_user.id).broadcast_typing_status = True


    @bot.message_handler(func= lambda message: get_user_status(message.from_user.id).broadcast_typing_status)
    @check_on_dev
    def send_broadcast(message: telebot.types.Message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) вызвал broadcast")
        get_user_status(message.from_user.id).broadcast_typing_status = False

        telegram_ids: tuple = db_obj.get_all_telegram_ids()

        for id in telegram_ids:
            try:
                user_settings = settings_db_obj.get_all_settings_by_telegram_id(id[0])

                if user_settings == None or type(user_settings) == int:
                    continue

                if user_settings.get("get_admin_brodcasts") == 1:
                    message_text = broadcast_prefix
                    bot.copy_message(id[0], message.chat.id, message.id)
                    time.sleep(1)
            
            except Exception as e:
                if "chat not found" in str(e):
                    logger.warning(f"При вызове broadcast, чат с id {id[0]} не был найден")
                    continue
                elif "user is deactivated" in str(e):
                    logger.warning(f"При вызове broadcast, аккаунт с id {id[0]} был деактивирован")
                    continue
                elif "bot was blocked by the user" in str(e):
                    logger.warning(f"При вызове broadcast, аккаунт с id {id[0]} заблокировал бота")
                    continue

                logger.critical(f"Ошибка при вызове broadcast: ", e)
                continue

        bot.send_message(message.chat.id, "✅ Broadcast успешно завершен")
                

def check_on_dev(func):
    def wrapper(message: telebot.types.CallbackQuery):
        if message.from_user.id in checked_admins:
            return func(message)
        
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) проверяется на права админа")

        if DEV_TELEGRAM_ID == None:
            logger.warning(f"Администратор не указан")

        if int(DEV_TELEGRAM_ID) != message.from_user.id:
            bot.send_message(message.chat.id, "Ты не админ, я тебя найду гандон чорт бля хули ты в админку ломишься пидарасина бля")
            return
        
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) прошел проверку на админа")
        checked_admins.append(message.from_user.id)

        return func(message)
    
    return wrapper



