import telebot
from ..core.states import get_user_status
from .authorization import check_auth
from ..core.generate_html_marks import generate_marks_page
from ..core.keyboards import make_return_button
from ..core.logs import logger

def setup_marks_module(bot: telebot.TeleBot):
    @bot.message_handler(func= lambda message: message.text == "5️⃣ Оценки")
    @check_auth
    def send_marks_menu(message: telebot.types.Message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) хочет посмотреть оценки")
        marks = get_user_status(message.from_user.id).API.get_marks()
        if type(marks) != list:
            bot.send_message(message.chat.id, "Ошибка смерти")
            return
        
        marks_page_url = generate_marks_page(marks)
        
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        see_marks_button = telebot.types.InlineKeyboardButton("Посмотреть", web_app=telebot.types.WebAppInfo(marks_page_url))
        keyboard.add(see_marks_button, make_return_button())
        bot.send_message(message.chat.id, "Оценки готовы к просмотру, нажмите на кнопку для их просмотра в привычном виде", reply_markup=keyboard)
        # bot.send_message(message.chat.id, "Оценки изза технических причин пока не работают, терпите")