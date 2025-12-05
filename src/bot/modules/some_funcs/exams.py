import telebot
from ..authorization import check_auth
from ...core.logs import logger
from ...core.states import get_user_status
from ...core.keyboards import make_return_keyboard
from ...core.pages import Pages, messages_pages
from ...core.journal_500 import get_500_message

def setup_exams_module(bot: telebot.TeleBot):
    @bot.callback_query_handler(func= lambda call: call.data == "show_future_exams")
    @check_auth
    def handle_get_future_exams(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) смотрит будущие экзмены")

        user = get_user_status(call.from_user.id)
        user_future_exams = user.API.get_future_exams()
        if user_future_exams == 500:
            bot.send_message(call.message.chat.id, get_500_message(call))
            return

        message = 'Экзамены\n\n'
        for exam in user_future_exams:

            exam_name = exam["spec"]
            exam_date = exam["date"]
            message += f"  <i>{exam_date}</i> - <b>{exam_name}</b>\n"
    

        bot.send_message(
            call.message.chat.id, 
            message, 
            parse_mode="HTML", 
            reply_markup=make_return_keyboard(), 
            disable_web_page_preview=True)

        
