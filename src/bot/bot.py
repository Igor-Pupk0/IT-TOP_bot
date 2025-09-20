import telebot
import datetime
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.Journal_API import API
from db.Journal_database import Creds_db


CONFIG_PATH = "src/bot/config.json"
users_states = {} # Состояния пользователей
user_auths = {} # Авторизированные пользователи

with open(CONFIG_PATH) as file:
    TOKEN = json.loads(file.read())["BOT_TOKEN"]

Bot = telebot.TeleBot(TOKEN)
db_obj = Creds_db()

###################################################
#   Функции для нормального функционирования бота #
###################################################

### Проверка авторизации
def check_auth(func):
    def wrapper(message):
        user_data = db_obj.get_all_by_telegram_id(message.from_user.id)
        user_states = users_states.get(message.from_user.id)

        if user_auths.get(message.from_user.id) == None and user_data != None:
            user_auths[message.from_user.id] = {"username": user_data[0], "password": user_data[1], "User_obj": None}
            user_auths[message.from_user.id]["User_obj"] = API(user_data[0], user_data[1], user_data[2])
        elif user_data[2] == 'None' or user_data[2] == None:
            print(12312)
            db_obj.update_user_JWT_token(user_data[0], user_auths[message.from_user.id]["User_obj"].JWT_TOKEN)


        if user_data == None and user_states == None:
            markup = telebot.types.InlineKeyboardMarkup()
            auth_button = telebot.types.InlineKeyboardButton("Авторизоваться", callback_data="auth")

            markup.add(auth_button)
            Bot.send_message(message.chat.id, "Авторизируйтесь!", reply_markup=markup)
            return
        return func(message)
    return wrapper

### Отправка расписания по дате в формате ISO
def send_schedule(message, iso_date):

    today_schedule = user_auths[message.from_user.id]["User_obj"].get_schedule_by_date(iso_date)
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


#####################################################################
#   ДАЛЕЕ ИДУТ ПЕРЕХВАТЧИКИ КОМАНД, СООБЩЕНИЙ И ВЫЗОВОВ (callbacks) #
#####################################################################


@Bot.message_handler(commands=['start'])
def start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)
    check_today_schedule_button = telebot.types.KeyboardButton("Посмотреть раписание на сегодня")
    check_tomorrow_schedule_button = telebot.types.KeyboardButton("Посмотреть раписание на завтра")

    keyboard.add(check_today_schedule_button, check_tomorrow_schedule_button)
    Bot.send_message(message.chat.id, "Это Айте топ бот, тут можно смотреть расписание", reply_markup=keyboard)


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
    Bot.send_message(message.chat.id, "Вхожу...")
    user_auths[message.from_user.id]["User_obj"] = API(user_auths[message.from_user.id]["username"], user_auths[message.from_user.id]["password"])

    if user_auths[message.from_user.id]["User_obj"].succesful_auth == False:
        Bot.send_message(message.chat.id, "Неправильные данные")
        user_auths.pop(message.from_user.id)
    else:
        Bot.send_message(message.chat.id, "Успешный вход!")
        db_obj.insert_user_creds(message.from_user.id, user_auths[message.from_user.id]["username"], user_auths[message.from_user.id]["password"])
        db_obj.update_user_JWT_token(user_auths[message.from_user.id]["username"], user_auths[message.from_user.id]["User_obj"].JWT_TOKEN)

        

### Инициализация авторизации
@Bot.callback_query_handler(func= lambda call: call.data == "auth" )
def user_auth(call):
    user_data = db_obj.get_all_by_telegram_id(call.from_user.id)

    if user_data != None:
        Bot.send_message(call.message.chat.id, "Ты уже авторизован!")
        return
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

if __name__ == "__main__":
    Bot.infinity_polling()