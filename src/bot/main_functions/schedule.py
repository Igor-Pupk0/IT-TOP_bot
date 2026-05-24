import aiogram
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
import datetime
from ..auth.authorization_callbacks import check_auth
from ..core.states import get_user_status
from ..core.logs import logger
from ..core.journal_500 import get_500_message
from ..core.pages import Keyboard_pages, messages_pages
from ..core.keyboards import make_return_button, make_turn_pages_buttons

schedule_router = aiogram.Router()

async def send_schedule(call: aiogram.types.CallbackQuery, iso_date):

    return_keyboard = InlineKeyboardBuilder()
    return_button = aiogram.types.InlineKeyboardButton(text="🔙 Назад", callback_data="return")
    return_keyboard.add(return_button)
    today_schedule = await (get_user_status(call.from_user.id).API.get_schedule_by_date(iso_date))
    if today_schedule == False:
        await call.message.answer(f"{iso_date}: пар нет")
        return
    elif today_schedule == 500:
        await call.message.answer(get_500_message(call.message))
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
    await call.answer()
    await call.message.answer(msg_to_send, parse_mode="HTML", reply_markup=return_keyboard.as_markup())
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) посмотрел расписание на {iso_date}")



### Отправить расписание
@schedule_router.callback_query(F.data.contains("_schedule"))
@check_auth
async def call_schedule(call):
    if "_day_schedule" in call.data:
        await send_schedule(call, call.data[:10])

### Список расписаний
@schedule_router.message(F.text == "📅 Раписание")
@check_auth
async def check_schedule(message: aiogram.types.Message):
    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) выбрал '{message.text}'")

    today_date = datetime.datetime.today()
    start_of_week_date = today_date - datetime.timedelta(days=today_date.weekday())

    keyboard_pages_obj = Keyboard_pages()
    for week_count in range(0, 3):

        # if week_count == 2:
        #     keyboard_pages_obj.turn_left_page()

        keyboard = InlineKeyboardBuilder()
        for weekday_number in range(0, 7):
            date_iso = start_of_week_date + datetime.timedelta(days=(weekday_number + (week_count * 7 - 7)))
            date_iso_text = date_iso.isoformat()[:10]
            date_iso_without_year = date_iso_text[5:]
            date_iso_button_text = f"{date_iso_without_year} ({match_weekday_num(date_iso.weekday())})"
            if weekday_number == today_date.weekday() and week_count == 1:
                date_iso_button_text = "Сегодня"

            schedule_button = aiogram.types.InlineKeyboardButton(text=date_iso_button_text, callback_data=f"{date_iso_text}_day_schedule")
            keyboard.add(schedule_button)

        button_turn_left, button_turn_right = make_turn_pages_buttons()
        keyboard.add(button_turn_left, button_turn_right, make_return_button())
        keyboard.adjust(1, 1, 1, 1, 1, 1, 1, 2, 1)
        keyboard_pages_obj.add_page(keyboard.as_markup())


    sended_message = await message.answer(text="Выберите дату:", reply_markup=keyboard_pages_obj.turn_right_page())
    messages_pages[message.from_user.id].update({sended_message.message_id: keyboard_pages_obj})

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