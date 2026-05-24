import aiogram
from aiogram import F
from ...auth.authorization_callbacks import check_auth
from ...core.logs import logger
from ....storage import settings_pages
from .settings_funcs import get_keyboard_markup
from .settings_funcs import switch_settings

get_homework_notifications_router = aiogram.Router()

@get_homework_notifications_router.callback_query(F.data == "settings_switch_get_alm_exp_hw")
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
    