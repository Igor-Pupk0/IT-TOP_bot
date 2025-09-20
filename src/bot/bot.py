import telebot
import datetime
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.Journal_API import API
from db.Journal_database import Creds_db
from user_states import User


CONFIG_PATH = "files/config.json"
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
        user_data: set = db_obj.get_all_by_telegram_id(message.from_user.id)
        user_states: User = users_states.get(message.from_user.id)

        if user_auths.get(message.from_user.id) == None and user_data != None:
            user_auths[message.from_user.id] = {"username": user_data[0], "password": user_data[1], "User_obj": None}
            user_auths[message.from_user.id]["User_obj"] = API(user_data[0], user_data[1], user_data[2])

        if user_data == None and user_states.auth_status == "No_auth":
            markup = telebot.types.InlineKeyboardMarkup()
            auth_button = telebot.types.InlineKeyboardButton("Авторизоваться", callback_data="auth")

            markup.add(auth_button)
            Bot.send_message(message.chat.id, "Авторизируйтесь!", reply_markup=markup)
            return
        if user_data[2] == 'None':
            db_obj.update_user_JWT_token(user_data[0], user_auths[message.from_user.id]["User_obj"].JWT_TOKEN)

        return func(message)
    return wrapper

### Отправка расписания по дате в формате ISO
def send_schedule(call, iso_date):

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
    Bot.send_message(call.message.chat.id, msg_to_send, parse_mode="HTML")


def get_user_status(telegram_id):
    user_states = users_states.get(telegram_id)

    if user_states != None:
        return user_states
    else:
        user_states = User()
        users_states[telegram_id] = user_states
        return user_states
    

#####################################################################
#   ДАЛЕЕ ИДУТ ПЕРЕХВАТЧИКИ КОМАНД, СООБЩЕНИЙ И ВЫЗОВОВ (callbacks) #
#####################################################################


@Bot.message_handler(commands=['start'])
def start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    check_today_schedule_button = telebot.types.KeyboardButton("📅 Посмотреть раписание")
    show_user_profile_button = telebot.types.KeyboardButton("🕵🏿‍♂️ Профиль")
    # check_tomorrow_schedule_button = telebot.types.KeyboardButton("Посмотреть раписание на завтра")

    keyboard.add(check_today_schedule_button, show_user_profile_button)
    Bot.send_message(message.chat.id, "Это Айте топ бот, тут можно смотреть расписание", reply_markup=keyboard)

### Авторизация
@Bot.message_handler(func=lambda message: get_user_status(message.from_user.id).auth_status == "Auth_on_username")
def auth_username(message):
    username = message.text
    users_states[message.from_user.id].auth_status = "No_auth"
    users_states[message.from_user.id].auth_status = "Auth_on_password"
    Bot.send_message(message.chat.id, "Пароль:")
    user_auths[message.from_user.id] = {"username": username, "password": None}


@Bot.message_handler(func=lambda message: users_states.get(message.from_user.id).auth_status == "Auth_on_password")
def auth_password(message):
    password = message.text
    users_states[message.from_user.id].auth_status = "No_auth"
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
    get_user_status(call.from_user.id).auth_status = "Auth_on_username"
    Bot.send_message(call.message.chat.id, "Логин:")
    
### Конец авторизации

### Выход из аккаунта
@Bot.callback_query_handler(func= lambda call: call.data == "logout" )
@check_auth
def logout(call):
    db_obj.delete_user_by_telegram_id(call.from_user.id)
    if user_auths.get(call.message.from_user.id) != None:
        user_auths.pop(call.message.from_user.id)
    Bot.send_message(call.message.chat.id, "Вы успешно вышли из аккаунта ✅")

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

    Bot.send_message(message.chat.id, "Выберите дату:", reply_markup=keyboard)

### Отправить рассписание
@Bot.callback_query_handler(func= lambda call: "_schedule" in call.data )
@check_auth
def user_auth(call):
    if "_day_schedule" in call.data:
        send_schedule(call, call.data[:10])

@Bot.message_handler(func=lambda message: True)
@check_auth
def handle_message(message):

    if message.text == "🕵🏿‍♂️ Профиль":
        profile_keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        logout_button = telebot.types.InlineKeyboardButton("Выйти из аккаунта ❌", callback_data="logout")

        profile_keyboard.add(logout_button)

        Bot.send_message(message.chat.id, "Твой профиль: бла бла бла скибиди жирни", reply_markup=profile_keyboard)


if __name__ == "__main__":
    Bot.infinity_polling()