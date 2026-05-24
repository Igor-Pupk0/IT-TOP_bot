import aiogram
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ....storage import settings_db_obj
from ...core.keyboards import make_return_button

async def get_keyboard_markup(telegram_id):
        responce = await settings_db_obj.get_all_settings_by_telegram_id(telegram_id)

        if responce.get('get_almost_expired_hw_notifications') == True:
            parametr_almost_expired_hw_notifictions = "✅"
        else:
            parametr_almost_expired_hw_notifictions = "❌"

        switch_get_almost_expired_hw_notifications = aiogram.types.InlineKeyboardButton(
            text=f"{parametr_almost_expired_hw_notifictions} Уведомления о просрочке дз", 
            callback_data="settings_switch_get_alm_exp_hw")

        if responce.get("get_admin_broadcasts") == True:
            parametr_get_admin_brodcasts = "✅"
        else:
            parametr_get_admin_brodcasts = "❌"

        switch_get_admin_broadcast = aiogram.types.InlineKeyboardButton(
            text=f"{parametr_get_admin_brodcasts} Оповещения", 
            callback_data="settings_switch_get_admin_bc")

        set_timezone = aiogram.types.InlineKeyboardButton(
            text=f"⏳ Часовой пояс ({responce.get("timezone")})", 
            callback_data="settings_set_timezone")

        keyboard = InlineKeyboardBuilder()
        keyboard.add(switch_get_almost_expired_hw_notifications, switch_get_admin_broadcast, set_timezone, 
                     make_return_button())
        keyboard.adjust(1)

        return keyboard.as_markup()

async def switch_settings(telegram_id, parametr):
    response = await settings_db_obj.get_all_settings_by_telegram_id(telegram_id)
    
    if response.get(parametr) == True:
        new_value = False
    else:
        new_value = True

    await settings_db_obj.update_user_settings(telegram_id, parametr, new_value)

