import telebot
from ..authorization import check_auth
from ...core.logs import logger
from ...core.keyboards import make_return_button

def setup_some_module(bot: telebot.TeleBot):
    @bot.message_handler(func=lambda message: message.text == "🐥 Разное")
    @check_auth
    def handle_message(message: telebot.types.Message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) выбрал '{message.text}'")

        profile_keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        logout_button = telebot.types.InlineKeyboardButton("👍 Оценка пар", callback_data="rate_all_lessons")
        feedbacks_button = telebot.types.InlineKeyboardButton("⭐️ Отзывы", callback_data="show_student_feedbacks")
        market_button = telebot.types.InlineKeyboardButton("💰 Маркет", callback_data="show_market")
        settings_button = telebot.types.InlineKeyboardButton("⚙️ Настройки", callback_data="show_settings_menu")
        leaderboads_button = telebot.types.InlineKeyboardButton("📈 Лидерборды", callback_data="show_leaderboards_menu")
        activity_button = telebot.types.InlineKeyboardButton("🪙 Активность", callback_data="show_activity")
        exams_button = telebot.types.InlineKeyboardButton("🥀 Экзамены", callback_data="show_future_exams")
        profile_keyboard.add(logout_button, feedbacks_button, market_button, settings_button, leaderboads_button, activity_button, exams_button, make_return_button())

        bot.send_message(message.chat.id,
                        f"Разные функции", 
                        reply_markup=profile_keyboard,
                        parse_mode="HTML")

