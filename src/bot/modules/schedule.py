import telebot
import datetime
from src.bot.modules.authorization import check_auth
from src.bot.core.storage import user_auths


def setup_schedule_module(Bot: telebot.TeleBot):

    ### Отправка расписания по дате в формате ISO
    def send_schedule(call, iso_date):

        return_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        return_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="return")
        return_keyboard.add(return_button)

        today_schedule = user_auths[call.from_user.id]["User_obj"].get_schedule_by_date(iso_date)
        if today_schedule == False:
            Bot.send_message(call.message.chat.id, f"{iso_date}: пар нет")
            return
        msg_to_send = f'Расписание на <b>{iso_date}</b>:\n\n'

        for lesson_json in today_schedule:
            lesson_number = lesson_json["lesson"]
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



    ### Отправить расписание
    @Bot.callback_query_handler(func= lambda call: "_schedule" in call.data )
    @check_auth
    def call_schedule(call):
        if "_day_schedule" in call.data:
            send_schedule(call, call.data[:10])

    ### Список расписаний
    @Bot.message_handler(func=lambda message: message.text == "📅 Посмотреть раписание")
    @check_auth
    def check_schedule(message):

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)

        today_date = datetime.datetime.today()

        for i in range(-1, 6):
            date_iso = (today_date + datetime.timedelta(days=i)).isoformat()[:10]
            date_iso_button_text = date_iso
            if i == -1:
                date_iso_button_text = "Вчера"
            elif i == 0:
                date_iso_button_text = "Сегодня"
            elif i == 1:
                date_iso_button_text = "Завтра"
            schedule_button = telebot.types.InlineKeyboardButton(date_iso_button_text, callback_data=f"{date_iso}_day_schedule")
            keyboard.add(schedule_button)

        return_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="return_main")
        keyboard.add(return_button)

        Bot.send_message(message.chat.id, "Выберите дату:", reply_markup=keyboard)

