import telebot
import datetime
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.Journal_API import API
from api.API_test import User

CONFIG_PATH = "src/bot/config.json"

with open(CONFIG_PATH) as file:
    TOKEN = json.loads(file.read())["BOT_TOKEN"]

users_states = {}
user_auths = {}



Bot = telebot.TeleBot(TOKEN)

def check_auth(func):
    def wrapper(message):
        user_dict = user_auths.get(message.from_user.id)
        user_states = users_states.get(message.from_user.id)

        if user_dict == None and user_states == None:
            markup = telebot.types.InlineKeyboardMarkup()
            auth_button = telebot.types.InlineKeyboardButton("Авторизоваться", callback_data="auth")

            markup.add(auth_button)
            Bot.send_message(message.chat.id, "Авторизируйтесь!", reply_markup=markup)
            return
        return func(message)
    return wrapper


@Bot.message_handler(commands=['start'])
def start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)
    check_today_schedule_button = telebot.types.KeyboardButton("Посмотреть раписание на сегодня")
    check_tomorrow_schedule_button = telebot.types.KeyboardButton("Посмотреть раписание на завтра")

    keyboard.add(check_today_schedule_button, check_tomorrow_schedule_button)
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
    Bot.send_message(message.chat.id, "Пароль:")
    user_auths[message.from_user.id] = {"username": username, "password": None}

@Bot.message_handler(func=lambda message: users_states.get(message.from_user.id) == "Auth_on_password")
def auth_password(message):
    password = message.text
    users_states.pop(message.from_user.id, None)
    user_auths[message.from_user.id]["password"] = password
    print(user_auths)
    Bot.send_message(message.chat.id, "Вхожу...")
    user_auths[message.from_user.id]["User_obj"] = API(user_auths[message.from_user.id]["username"], user_auths[message.from_user.id]["password"])

    if user_auths[message.from_user.id]["User_obj"].succesful_auth == False:
        Bot.send_message(message.chat.id, "Неправильные данные")
        user_auths.pop(message.from_user.id)
    else:
        Bot.send_message(message.chat.id, "Успешный вход!")



@Bot.callback_query_handler(func= lambda call: call.data == "auth" )
def user_auth(call):
    user_dict = user_auths.get(call.message.from_user.id)

    if user_dict != None:
        Bot.send_message(call.message.chat.id, "Ты уже авторизован!")
    users_states[call.from_user.id] = "Auth_on_username"
    Bot.send_message(call.message.chat.id, "Логин:")
    


@Bot.message_handler(func=lambda message: True)
@check_auth
def handle_message(message):

    if message.text == 'Посмотреть раписание на сегодня':
        iso_date = datetime.datetime.today().isoformat()[:10]
        send_schedule(message, iso_date)

    elif message.text == "Посмотреть раписание на завтра":
        iso_date = (datetime.datetime.today() + datetime.timedelta(days=1)).isoformat()[:10]
        send_schedule(message, iso_date)

Bot.infinity_polling()