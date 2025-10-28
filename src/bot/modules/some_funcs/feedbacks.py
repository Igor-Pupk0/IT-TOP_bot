import telebot
from ..authorization import check_auth
from ...core.logs import logger
from ...core.states import get_user_status
from ...core.pages import Pages, messages_pages
from ...core.keyboards import make_return_button
from ...core.journal_500 import get_500_message
from ...core.keyboards import make_return_button, make_turn_pages_buttons

def setup_get_feedbacks_module(bot: telebot.TeleBot):
    @bot.callback_query_handler(func= lambda call: call.data == "show_student_feedbacks")
    @check_auth
    def handle_get_feedbacks(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) смотрит отзывы о себе")

        user_feedbacks: list = get_user_status(call.from_user.id).API.get_student_feedbacks()
        
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        turn_left_button, turn_right_button = make_turn_pages_buttons()
        keyboard.add(turn_left_button, turn_right_button, make_return_button())
        pages_obj = Pages()
        user_feedbacks.reverse()
        
        for num, fb in enumerate(user_feedbacks):
            fb_message = fb["message"]
            fb_spec = fb["full_spec"]
            fb_prepod = fb["teacher"]
            fb_date = fb["date"]

            pages_obj.add_page(f"""\
Отзыв №{num+1} из {len(user_feedbacks)}

    Дата: <i>{fb_date}</i>
    От: <b>{fb_prepod}</b>
    Предмет: <b>{fb_spec}</b>

    <i>{fb_message}</i>
""")

        sended_message: telebot.types.Message = bot.send_message(
            call.message.chat.id, 
            pages_obj.get_page(), 
            parse_mode="HTML", 
            reply_markup=keyboard, 
            disable_web_page_preview=True)
        
        messages_pages[call.from_user.id] = {sended_message.message_id: pages_obj}