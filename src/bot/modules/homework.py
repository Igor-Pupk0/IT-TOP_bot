import telebot
import datetime

from src.bot.core.storage import user_auths
from src.bot.core.authorization import check_auth

def setup_homework_module(Bot):

    ### Отправить рассписание
    @Bot.callback_query_handler(func= lambda call: "_homework_show" in call.data )
    @check_auth
    def call_send_homework(call):
        today_date = datetime.datetime.today().isoformat()[:10]
        homework_message_to_send = ''

        return_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        return_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="return")
        return_keyboard.add(return_button)

        match call.data:
            case "0_homework_show":
            #   homework: dict = user_auths[call.from_user.id]["User_obj"].get_homework(0, 1)
            #   homework_message_to_send = "Так как создатель бота прилежный студент, у меня нет просроченного ДЗ и я не могу пропарсить json ответ, чтобы добавить его просмотр сюда"
                homework_message_to_send = "В разработке"
                
            case "1_homework_show":
                marked_homework: dict = user_auths[call.from_user.id]["User_obj"].get_homework(1, 1)
                homework_message_to_send = f"Оценки за дз на <b>{today_date}:</b>\n\n"

                for hw in marked_homework:
                    start_date = hw["creation_time"]
                    done_date = hw["homework_stud"]["creation_time"]
                    lesson_name = hw["name_spec"]
                    theme = hw["theme"]
                    homework_file_path = hw["homework_stud"]["file_path"]
                    mark = hw["homework_stud"]["mark"]
                    comment = hw["homework_comment"]["text_comment"]

                    clickable_file = f'<a href="{homework_file_path}">ТЫК</a>'
                    if homework_file_path == None:
                        clickable_file = "<i>Отсутствует</i>"
                    else:
                        clickable_file = f'<a href="{homework_file_path}">ТЫК</a>'

                    if comment == None:
                        comment = "Отсутствует"

                    homework_message_to_send += f"""\
    ДЗ по {lesson_name}:
    Тема: <i>{theme}</i>
    - Когда задали: <b>{start_date}</b>
    - Сдано: <b>{done_date}</b>
    - Оценка: <b>{mark}</b>
    - Файл с ДЗ: {clickable_file}
    Комментарий по дз от препода: <i>{comment}</i>

    """
        

            case "2_homework_show":
                waited_homework: dict = user_auths[call.from_user.id]["User_obj"].get_homework(2, 1)
                homework_message_to_send = f"ДЗ, ожидающие проверки на <b>{today_date}:</b>\n\n"

                for hw in waited_homework:
                    start_date = hw["creation_time"]
                    end_date = hw["completion_time"]
                    done_date = hw["homework_stud"]["creation_time"]

                    lesson_name = hw["name_spec"]
                    theme = hw["theme"]
                    homework_file_path = hw["file_path"]
                    comment = hw["comment"]
                    clickable_file = f'<a href="{homework_file_path}">ТЫК</a>'

                    if homework_file_path == None:
                        clickable_file = "<i>Отсутствует</i>"
                    else:
                        clickable_file = f'<a href="{homework_file_path}">ТЫК</a>'

                    if comment == None:
                        comment = "Отсутствует"

                    homework_message_to_send += f"""\
    ДЗ по {lesson_name}:
    Тема: <i>{theme}</i>
    - Когда задали: <b>{start_date}</b>
    - Сдано: <b>{done_date}</b>
    - Крайний день: <b>{end_date}</b>
    - Файл с ДЗ: {clickable_file}
    Комментарий: <i>{comment}</i>
    
    """




            case "3_homework_show":
                actual_homework: dict = user_auths[call.from_user.id]["User_obj"].get_homework(3, 1)
                homework_message_to_send = f"Актуальное дз на <b>{today_date}:</b>\n\n"

                for hw in actual_homework:
                    start_date = hw["creation_time"]
                    end_date = hw["completion_time"]
                    lesson_name = hw["name_spec"]
                    theme = hw["theme"]
                    pinned_file_path = hw["file_path"]
                    banner_image_path = hw["cover_image"]
                    comment = hw["comment"]
                    if comment == "":
                        comment = "Отсутствует"

                    homework_message_to_send += f"""\
    ДЗ по {lesson_name}:
    Тема: <i>{theme}</i>
    - Когда задали: <b>{start_date}</b>
    - До какого надо сделать: <b>{end_date}</b>
    - Прикрепленный файл: <a href="{pinned_file_path}">ТЫК</a>
    Комментарий: <i>{comment}</i>

    """
                
        Bot.send_message(call.message.chat.id, homework_message_to_send, parse_mode="HTML", reply_markup=return_keyboard, disable_web_page_preview=True)





    ### Список ДЗ
    @Bot.message_handler(func=lambda message: message.text == "📔 Посмотреть ДЗ")
    @check_auth
    def check_homeworks(message):

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)


        homework0_button = telebot.types.InlineKeyboardButton("✖️ Просроченное", callback_data=f"0_homework_show")
        homework1_button = telebot.types.InlineKeyboardButton("✔️ Оцененное", callback_data=f"1_homework_show")
        homework2_button = telebot.types.InlineKeyboardButton("⏳ На проверке", callback_data=f"2_homework_show")
        homework3_button = telebot.types.InlineKeyboardButton("🖊 Актуальное", callback_data=f"3_homework_show")
        return_button = return_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="return_main")
        keyboard.add(homework0_button, homework1_button, homework2_button, homework3_button, return_button)

        Bot.send_message(message.chat.id, "Выберите тип ДЗ которое вы хотите посмотреть:", reply_markup=keyboard)
