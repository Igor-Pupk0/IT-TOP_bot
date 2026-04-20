import telebot
from ..core.states import get_user_status
from .authorization import check_auth
from ..core.generate_html_marks import generate_marks_page
from ..core.keyboards import make_return_button
from ..core.logs import logger
from ..core.journal_500 import get_500_message

def setup_marks_module(bot: telebot.TeleBot):
    @bot.message_handler(func= lambda message: message.text == "5️⃣ Оценки")
    @check_auth
    def send_marks_menu(message: telebot.types.Message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) хочет посмотреть оценки")
        marks = get_user_status(message.from_user.id).API.get_marks()
        if marks == 500:
            bot.send_message(message.chat.id, get_500_message(message))
            return
        elif type(marks) != list:
            bot.send_message(message.chat.id, "Ошибка")
            return
        
        marks_page_url = generate_marks_page(marks)
        
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text='Открыть', web_app=telebot.types.WebAppInfo(url=marks_page_url)))
        keyboard.add(make_return_button())
        bot.send_message(message.chat.id, f"Оценки готовы к просмотру", reply_markup=keyboard)