import aiogram
from aiogram import F
from ...auth.authorization_callbacks import check_auth
from ...core.logs import logger
from ....storage import settings_db_obj, settings_pages
from .timezone import timezone_router
from .settings_funcs import get_keyboard_markup
from .get_homework_notifications import get_homework_notifications_router
from .get_broadcast import get_broadcast_router

settings_router = aiogram.Router()
settings_router.include_routers(
    timezone_router,
    get_homework_notifications_router,
    get_broadcast_router
)

@settings_router.callback_query(F.data == "show_settings_menu")
@check_auth
async def handle_get_settings(call: aiogram.types.CallbackQuery):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) смотрит настройки")

    user_settings: dict = await settings_db_obj.get_all_settings_by_telegram_id(call.from_user.id)
    message = "Настройки бота"

    await call.answer()
    sended_message = await call.message.answer(
        text=message, 
        parse_mode="HTML", 
        reply_markup=await get_keyboard_markup(call.from_user.id), 
        disable_web_page_preview=True)
    
    settings_pages[call.from_user.id] = sended_message
    
    


