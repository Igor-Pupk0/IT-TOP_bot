import aiogram
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..auth.authorization_callbacks import check_auth
from ..core.logs import logger
from ...storage import settings_db_obj
from ..core.keyboards import make_return_button
from ..core.keyboards import make_return_button

settings_pages = {}

settings_router = aiogram.Router()

@settings_router.callback_query(F.data == "show_settings_menu")
@check_auth
async def handle_get_settings(call: aiogram.types.CallbackQuery):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) смотрит настройки")

    user_settings: dict = await settings_db_obj.get_all_settings_by_telegram_id(call.from_user.id)
    logger.info(f"{user_settings}")
    message = "Настройки бота"

    sended_message = await call.message.answer(
        text=message, 
        parse_mode="HTML", 
        reply_markup=await get_keyboard_markup(call.from_user.id), 
        disable_web_page_preview=True)
    
    settings_pages[call.from_user.id] = sended_message
    
    
@settings_router.callback_query(F.data == "settings_switch_get_alm_exp_hw")
@check_auth
async def handle_switch_almost_expired_hw_notif(call: aiogram.types.CallbackQuery):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) сменил в настройках уведомления о просрочке дз")

    await switch_settings(call.from_user.id, "get_almost_expired_hw_notifications")
    message: aiogram.types.Message = settings_pages.get(call.from_user.id)

    if message == None:
        await call.message.answer(text="Ошибка, вызовите меню еще раз", show_alert=True)
        return
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=await get_keyboard_markup(call.from_user.id))

@settings_router.callback_query(F.data == "settings_switch_get_admin_bc")
@check_auth
async def handle_switch_admin_bc(call: aiogram.types.CallbackQuery):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) сменил в настройках получение админ-оповещений")

    await switch_settings(call.from_user.id, "get_admin_broadcasts")
    message: aiogram.types.Message = settings_pages.get(call.from_user.id)

    if message == None:
        await call.message.answer(text="Ошибка, вызовите меню еще раз", show_alert=True)
        return
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=await get_keyboard_markup(call.from_user.id))
    

async def switch_settings(telegram_id, parametr):
    response = await settings_db_obj.get_all_settings_by_telegram_id(telegram_id)
    
    if response.get(parametr) == True:
        new_value = False
    else:
        new_value = True

    await settings_db_obj.update_user_settings(telegram_id, parametr, new_value)

async def get_keyboard_markup(telegram_id):
        responce = await settings_db_obj.get_all_settings_by_telegram_id(telegram_id)
        
        keyboard = InlineKeyboardBuilder()

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

        switch_get_admin_broadcast = aiogram.types.InlineKeyboardButton(text=f"{parametr_get_admin_brodcasts} Оповещения от админа", 
                                                                        callback_data="settings_switch_get_admin_bc")

        keyboard.add(switch_get_almost_expired_hw_notifications, switch_get_admin_broadcast, make_return_button())
        keyboard.adjust(2)

        return keyboard.as_markup()