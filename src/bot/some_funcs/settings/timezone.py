import aiogram
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from ...auth.authorization_callbacks import check_auth
from ...core.logs import logger
from ....storage import settings_db_obj, settings_pages
from .settings_funcs import get_keyboard_markup

class TimezoneState(StatesGroup):
    waiting_timezone = State()

timezone_router = aiogram.Router()

@timezone_router.callback_query(F.data == "settings_set_timezone")
@check_auth
async def handle_set_timezone(call: aiogram.types.CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) хочет сменить таймзону")
    
    keyboard = InlineKeyboardBuilder()
    cancel_button = aiogram.types.InlineKeyboardButton(text="❌ Отмена", callback_data="return_broadcast")
    keyboard.add(cancel_button)

    await state.set_state(TimezoneState.waiting_timezone)
    await call.answer()
    await call.message.answer(
        text="Введи свой часовой пояс относительно МСК в формате +/-4 (например: -1, +3, 0). Он влияет на время отправки уведомлений о дз",
        reply_markup=keyboard.as_markup())
    
@timezone_router.message(TimezoneState.waiting_timezone)
@check_auth
async def set_timezone(message: aiogram.types.Message, state: FSMContext):
    await state.clear()

    checked_timezone = ''

    if len(message.text) == 1 and message.text[0].isdigit():
        checked_timezone = message.text
    elif len(message.text) == 2 and (message.text[1].isdigit() and message.text[0] in ['+', "-"]):
        checked_timezone = message.text
    else:
        await message.answer(text="Неправильный формат, попробуй еще раз")
        return

    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) сменил в настройках таймзону на {message.text}")

    await settings_db_obj.update_user_settings(message.from_user.id, "timezone", checked_timezone)

    menu_message = "Настройки бота"

    sended_message = await message.answer(
        text=menu_message, 
        parse_mode="HTML", 
        reply_markup=await get_keyboard_markup(message.from_user.id), 
        disable_web_page_preview=True)
    
    settings_pages[message.from_user.id] = sended_message