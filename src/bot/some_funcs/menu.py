import aiogram
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..auth.authorization_callbacks import check_auth
from ..core.logs import logger
from ..core.keyboards import make_return_button

from .rate_all_lessons import rate_lessons_router
from .market import market_router
from .exams import exams_router
from .feedbacks import feedbacks_router
from .leaderboards import leaderboards_router
from .activity import activity_router
from .settings.settings import settings_router

some_menu_router = aiogram.Router()
some_menu_router.include_routers(
    rate_lessons_router,
    market_router,
    exams_router,
    feedbacks_router,
    leaderboards_router,
    activity_router,
    settings_router
)

@some_menu_router.message(F.text == "🐥 Разное")
@check_auth
async def handle_message(message: aiogram.types.Message):
    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) выбрал '{message.text}'")

    profile_keyboard = InlineKeyboardBuilder()
    logout_button = aiogram.types.InlineKeyboardButton(text="👍 Оценка пар", callback_data="rate_all_lessons")
    feedbacks_button = aiogram.types.InlineKeyboardButton(text="⭐️ Отзывы", callback_data="show_student_feedbacks")
    market_button = aiogram.types.InlineKeyboardButton(text="💰 Маркет", callback_data="show_market")
    settings_button = aiogram.types.InlineKeyboardButton(text="⚙️ Настройки", callback_data="show_settings_menu")
    leaderboads_button = aiogram.types.InlineKeyboardButton(text="📈 Лидерборды", callback_data="show_leaderboards_menu")
    activity_button = aiogram.types.InlineKeyboardButton(text="🪙 Активность", callback_data="show_activity")
    exams_button = aiogram.types.InlineKeyboardButton(text="🥀 Экзамены", callback_data="show_future_exams")
    profile_keyboard.add(logout_button, feedbacks_button, market_button, settings_button, leaderboads_button, activity_button, exams_button, make_return_button())
    profile_keyboard.adjust(2)

    await message.answer(
        text=f"Разные функции", 
        reply_markup=profile_keyboard.as_markup(),
        parse_mode="HTML")

