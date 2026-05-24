import aiogram
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ...auth.authorization_callbacks import check_auth
from ...core.logs import logger
from ...core.states import get_user_status, delete_user_status
from ...core.keyboards import make_return_button
from ...core.journal_500 import get_500_message
from ....storage import db_obj
from .statistic import static_router

profile_router = aiogram.Router()
profile_router.include_router(static_router)

@profile_router.message(F.text == "🕵🏿‍♂️ Профиль")
@check_auth
async def handle_message(message: aiogram.types.Message):
    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) выбрал '{message.text}'")

    profile_keyboard = InlineKeyboardBuilder()
    logout_button = aiogram.types.InlineKeyboardButton(text="❌ Выйти из аккаунта", callback_data="logout")
    statistic_button = aiogram.types.InlineKeyboardButton(text="📊 Статистика ", callback_data="show_statistic")
    profile_keyboard.add(statistic_button, logout_button, make_return_button())
    profile_keyboard.adjust(2, 1)

    user = get_user_status(message.from_user.id)
    
    user_info = await user.API.get_user_info()
    if user_info == 500:
        await message.answer(get_500_message(message))
        return

    ### Дикое извлечение данных
    full_name = user_info["full_name"]
    name = full_name.split()[1]
    group_name = user_info["group_name"]

    topcoins = user_info["gaming_points"][0]["points"]
    topgems = user_info["gaming_points"][1]["points"]

    await message.answer(f"""\
Твой профиль:
Привет, <b>{name}</b>
Твоя группа: {group_name}

Баланс:
- <b>{topcoins}</b> Топкоинов 💸
- <b>{topgems}</b> Топгемов  💎

""", 
                    reply_markup=profile_keyboard.as_markup(),
                    parse_mode="HTML")


async def logout(telegram_id):
    logger.info(f"Пользователь (???:{telegram_id}) был кикнут из аккаунта")
    await db_obj.delete_user_by_telegram_id(telegram_id)
    delete_user_status(telegram_id)