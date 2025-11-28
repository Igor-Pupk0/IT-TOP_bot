import telebot
import datetime
from ..modules.authorization import check_auth
from ..core.states import get_user_status
from ..core.logs import logger
from ..core.journal_500 import get_500_message
from ..core.pages import Keyboard_pages, messages_pages
from ..core.keyboards import make_return_button, make_turn_pages_buttons


def setup_schedule_module(Bot: telebot.TeleBot):

    ### Отправка расписания по дате в формате ISO
    def send_schedule(call: telebot.types.CallbackQuery, iso_date):

        return_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        return_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="return")
        return_keyboard.add(return_button)

        today_schedule = get_user_status(call.from_user.id).API.get_schedule_by_date(iso_date)
        if today_schedule == False:
            Bot.send_message(call.message.chat.id, f"{iso_date}: пар нет")
            return
        elif today_schedule == 500:
            Bot.send_message(call.from_user.id, get_500_message(call.message))
            return

        msg_to_send = f'Расписание на <b>{iso_date}</b>:\n\n'

        tmp_lesson_number = 1488

        for lesson_json in today_schedule:

            lesson_number = lesson_json["lesson"]
            if tmp_lesson_number + 1 < lesson_number:
                msg_to_send += """\
        <b>ОКНО</b>

"""
            lesson_number = lesson_json["lesson"]
            tmp_lesson_number = lesson_number
            start_time = lesson_json["started_at"]
            end_time = lesson_json["finished_at"]
            teacher = lesson_json["teacher_name"]
            subject = lesson_json["subject_name"]
            where = lesson_json["room_name"]

            msg_to_send += f"""\
    Пара №{lesson_number} ({subject}):
        - Время: <b>{start_time} - {end_time}</b>
        - Ведет: <b>{teacher}</b>
        - Кабинет: <b>{where}</b>
                
    """
        Bot.send_message(call.message.chat.id, msg_to_send, parse_mode="HTML", reply_markup=return_keyboard)
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) посмотрел расписание на {iso_date}")



    ### Отправить расписание
    @Bot.callback_query_handler(func= lambda call: "_schedule" in call.data )
    @check_auth
    def call_schedule(call):
        if "_day_schedule" in call.data:
            send_schedule(call, call.data[:10])

    ### Список расписаний
    @Bot.message_handler(func=lambda message: message.text == "📅 Раписание")
    @check_auth
    def check_schedule(message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) выбрал '{message.text}'")
        

        today_date = datetime.datetime.today()
        start_of_week_date = today_date - datetime.timedelta(days=today_date.weekday())

        keyboard_pages_obj = Keyboard_pages()
        for week_count in range(0, 3):

            # if week_count == 2:
            #     keyboard_pages_obj.turn_left_page()

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
            for i in range(0, 7):
                date_iso = start_of_week_date + datetime.timedelta(days=(i + (week_count * 7 - 7)))
                date_iso_text = date_iso.isoformat()[:10]
                date_iso_without_year = date_iso_text[5:]
                date_iso_button_text = f"{date_iso_without_year} ({match_weekday_num(date_iso.weekday())})"
                if i == today_date.weekday() and week_count == 1:
                    date_iso_button_text = "Сегодня"

                schedule_button = telebot.types.InlineKeyboardButton(date_iso_button_text, callback_data=f"{date_iso_text}_day_schedule")
                keyboard.add(schedule_button)


            keyboard_pages_obj.add_page(keyboard)
        
        

            button_turn_left, button_turn_right = make_turn_pages_buttons()
            keyboard.add(button_turn_left, button_turn_right, make_return_button())

        sended_message = Bot.send_message(message.chat.id, "Выберите дату:", reply_markup=keyboard_pages_obj.turn_right_page())
        messages_pages[message.from_user.id] = {sended_message.message_id: keyboard_pages_obj}

def match_weekday_num(weekday_num: int) -> str:
    match weekday_num:
        case 0:
            return "Пн"
        case 1:
            return "Вт"
        case 2:
            return "Ср"
        case 3:
            return "Чт"
        case 4:
            return "Пт"
        case 5:
            return "Сб"
        case 6:
            return "Вс"
        
    return "??"