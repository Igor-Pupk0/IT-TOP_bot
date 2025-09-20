import telebot
import datetime
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from api.Journal_API import API
from api.API_test import User

CONFIG_PATH = "src/bot/config.json"

with open(CONFIG_PATH) as file:
    TOKEN = json.loads(file.read())["BOT_TOKEN"]

users_states = {}




Bot = telebot.TeleBot(TOKEN)

@Bot.message_handler(commands=['start'])
def start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)
    check_today_schedule_button = telebot.types.KeyboardButton("Посмотреть раписание на сегодня")
    check_tomorrow_schedule_button = telebot.types.KeyboardButton("Посмотреть раписание на завтра")
    auth_button = telebot.types.KeyboardButton("Авторизоваться")

    keyboard.add(check_today_schedule_button, check_tomorrow_schedule_button, auth_button)
    Bot.send_message(message.chat.id, "Это Айте топ бот, тут можно смотреть расписание", reply_markup=keyboard)

def send_schedule(message, iso_date):

    today_schedule = User.get_schedule_by_date(iso_date)
    if today_schedule == False:
        Bot.send_message(message.chat.id, "В этот день пар нет", parse_mode="MarkdownV2")
        return
    msg_to_send = ''

    for lesson_json in today_schedule:
        lesson_number = lesson_json["lesson"]
        start_time = lesson_json["started_at"]
        end_time = lesson_json["finished_at"]
        teacher = lesson_json["teacher_name"]
        subject = lesson_json["subject_name"]
        where = lesson_json["room_name"]

        msg_to_send += f"""\
Пара №{lesson_number} \\({subject}\\):
    \\- Время: *{start_time} \\- {end_time}*
    \\- Ведет: *{teacher}*
    \\- Кабинет: *{where}*
            
"""

    Bot.send_message(message.chat.id, msg_to_send, parse_mode="MarkdownV2")

@Bot.message_handler(func=lambda message: users_states.get(message.from_user.id) == "Auth_on_username")
def auth_username(message):
    username = message.text
    users_states.pop(message.from_user.id, None)
    users_states[message.from_user.id] = "Auth_on_password"
    Bot.reply_to(message, "Пароль:")
    print(username)

@Bot.message_handler(func=lambda message: users_states.get(message.from_user.id) == "Auth_on_password")
def auth_password(message):
    password = message.text
    users_states.pop(message.from_user.id, None)
    print(password)



@Bot.message_handler(func=lambda message: True)
def handle_message(message):

    if message.text == 'Посмотреть раписание на сегодня':
        iso_date = datetime.datetime.today().isoformat()[:10]
        send_schedule(message, iso_date)

    elif message.text == "Посмотреть раписание на завтра":
        iso_date = (datetime.datetime.today() + datetime.timedelta(days=1)).isoformat()[:10]
        send_schedule(message, iso_date)
    elif message.text == "Авторизоваться":
        users_states[message.from_user.id] = "Auth_on_username"
        Bot.reply_to(message, "Логин:")
        # @Bot.message_handler(func=lambda message: True)
        # def get_login(message1):
        #     username = message1.text
        #     Bot.reply_to(message, "Пароль:")
        #     @Bot.message_handler(func=lambda message: True)
        #     def get_pass(message2):
        #         password = message2.text
        #         print(username, password)
        #         Bot.send_message(message.chat.id, "Вхожу")


Bot.infinity_polling()