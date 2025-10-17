import telebot
from ..authorization import check_auth
from ...core.logs import logger
from ...core.states import get_user_status
from ...core.keyboards import make_return_button
from ...core.journal_500 import get_500_message

def setup_rate_lessons_module(bot: telebot.TeleBot):
    @bot.callback_query_handler(func= lambda call: call.data == "rate_all_lessons")
    @check_auth
    def handle_rate_lessons(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) хочет оценить все занятия")
        
        user = get_user_status(call.from_user.id)
        user_lessons = user.API.get_lessons_for_feedback()

        if user_lessons == 500:
            get_500_message(call.message)
            return

        if user_lessons == None or user_lessons == []:
            bot.send_message(call.message.chat.id, "Пар на оценку нет")
            return
        
        count = 0
        for lesson in user_lessons:
            user.API.send_lesson_feedback(lesson.get("key"))
            count += 1


        bot.send_message(call.chat.id,
                        f"Было оценено <i>{count}</i> пар!", 
                        parse_mode="HTML")

