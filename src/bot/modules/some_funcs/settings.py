import telebot
from ..authorization import check_auth
from ...core.logs import logger
from ...core.storage import settings_db_obj
from ...core.keyboards import make_return_button
from ...core.keyboards import make_return_button

settings_pages = {}

def setup_settings_module(bot: telebot.TeleBot):
    @bot.callback_query_handler(func= lambda call: call.data == "show_settings_menu")
    @check_auth
    def handle_get_settings(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) смотрит настройки")

        user_settings: tuple = settings_db_obj.get_all_settings_by_telegram_id(call.from_user.id)
        message = "Настройки бота"

        if user_settings == None:
            settings_db_obj.init_user_settings(call.from_user.id)

        sended_message = bot.send_message(
            call.message.chat.id, 
            message, 
            parse_mode="HTML", 
            reply_markup=get_keyboard_markup(call.from_user.id), 
            disable_web_page_preview=True)
        
        settings_pages[call.from_user.id] = sended_message
        
        
    @bot.callback_query_handler(func= lambda call: call.data == "settings_switch_get_alm_exp_hw")
    @check_auth
    def handle_switch_almost_expired_hw_notif(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) сменил в настройках уведомления о просрочке дз")

        switch_settings(call.from_user.id, "get_almost_expired_hw_notifictions")
        message: telebot.types.Message = settings_pages.get(call.from_user.id)

        if message == None:
            bot.answer_callback_query(call.id, "Ошибка, вызовите меню еще раз", show_alert=True)
            return

        bot.edit_message_reply_markup(message.chat.id, message.id, reply_markup=get_keyboard_markup(call.from_user.id))

    @bot.callback_query_handler(func= lambda call: call.data == "settings_switch_get_admin_bc")
    @check_auth
    def handle_switch_admin_bc(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) сменил в настройках получение админ-оповещений")

        switch_settings(call.from_user.id, "get_admin_brodcasts")
        message: telebot.types.Message = settings_pages.get(call.from_user.id)

        if message == None:
            bot.answer_callback_query(call.id, "Ошибка, вызовите меню еще раз", show_alert=True)
            return
        bot.edit_message_reply_markup(message.chat.id, message.id, reply_markup=get_keyboard_markup(call.from_user.id))
        
        
    

def switch_settings(telegram_id, parametr):
    responce = settings_db_obj.get_all_settings_by_telegram_id(telegram_id)
    print(responce)

    if responce.get(parametr) == True:
        new_value = False
    else:
        new_value = True

    settings_db_obj.update_user_settings(telegram_id, parametr, new_value)

def get_keyboard_markup(telegram_id):
        responce = settings_db_obj.get_all_settings_by_telegram_id(telegram_id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)

        if responce.get('get_almost_expired_hw_notifictions') == True:
            parametr_almost_expired_hw_notifictions = "✅"
        else:
            parametr_almost_expired_hw_notifictions = "❌"

        switch_get_almost_expired_hw_notifications = telebot.types.InlineKeyboardButton(f"{parametr_almost_expired_hw_notifictions} Уведомления о просрочке дз", 
                                                                                        callback_data="settings_switch_get_alm_exp_hw")

        if responce.get('get_admin_brodcasts') == True:
            parametr_get_admin_brodcasts = "✅"
        else:
            parametr_get_admin_brodcasts = "❌"

        switch_get_admin_broadcast = telebot.types.InlineKeyboardButton(f"{parametr_get_admin_brodcasts} Оповещения от админа", 
                                                                        callback_data="settings_switch_get_admin_bc")

        keyboard.add(switch_get_almost_expired_hw_notifications, switch_get_admin_broadcast, make_return_button())

        return keyboard