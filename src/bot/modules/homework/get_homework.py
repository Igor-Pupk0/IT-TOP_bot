import telebot
import datetime

from ..authorization import check_auth
from ...core.pages import Pages, messages_pages
from ...core.keyboards import make_return_button, make_turn_pages_buttons
from ...core.logs import logger
from ...core.journal_500 import get_500_message
from ...core.states import get_user_status


def generate_homeworks_page(telegram_id, pages_obj: Pages, homework_type, page):
    today_date = datetime.datetime.today().isoformat()[:10]
    homework_message_to_send = ''

    homework_count = get_user_status(telegram_id).API.get_homework_count()

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    turn_left_button, turn_right_button = make_turn_pages_buttons()
    keyboard.add(turn_left_button, turn_right_button)
    
    if homework_type == 3 or homework_type == 0:
        send_homework_button = telebot.types.InlineKeyboardButton("📚 Сдать ДЗ", callback_data="send_homework_menu")
        keyboard.add(send_homework_button)


    elif homework_type == 5 or homework_type == 1:
        send_homework_button = telebot.types.InlineKeyboardButton("📚 Пересдать", callback_data="send_homework_menu")
        keyboard.add(send_homework_button)
    
    elif homework_type == 2:
        send_homework_button = telebot.types.InlineKeyboardButton("❌ Удалить", callback_data="delete_homework")
        keyboard.add(send_homework_button)

    keyboard.add(make_return_button())

    match homework_type:
        case 0:
            homework_message_to_send = f"Просроченное дз на <b>{today_date}:</b>\n\n"
            pages_count = homework_count["type_0"] // 6 + 2

            actual_homework: dict = get_user_status(telegram_id).API.get_homework(0, page)
            for hw in actual_homework:
                start_date = hw["creation_time"]
                end_date = hw["completion_time"]
                lesson_name = hw["name_spec"]
                theme = hw["theme"]
                pinned_file_path = hw["file_path"]
                banner_image_path = hw["cover_image"]
                comment = hw["comment"]

                homework_id = hw["id"]

                if comment == "":
                    comment = "Отсутствует"

                pages_obj.add_page(f"""\
Страница: №{pages_obj.page_count + 1} из {homework_count["type_0"]}

ДЗ по {lesson_name}:
Тема: <i>{theme}</i>
- Когда задали: <b>{start_date}</b>
- До какого надо сделать: <b>{end_date}</b>
- Прикрепленный файл: <a href="{pinned_file_path}">ТЫК</a>
Комментарий: <i>{comment}</i>

""", {"homework_id": homework_id, "lesson_name": lesson_name})
            
        case 1:
            homework_message_to_send = f"Оценки за дз на <b>{today_date}:</b>"
            pages_count = homework_count["type_1"] // 6 + 2

            marked_homework = get_user_status(telegram_id).API.get_homework(1, page)


            for hw in marked_homework:
                start_date = hw["creation_time"]
                done_date = hw["homework_stud"]["creation_time"]
                lesson_name = hw["name_spec"]
                theme = hw["theme"]
                pinned_file_path = hw["file_path"]
                homework_file_path = hw["homework_stud"]["file_path"]
                mark = hw["homework_stud"]["mark"]
                comment = hw["homework_comment"]["text_comment"]
                text_answer = hw["homework_stud"]["stud_answer"]


                homework_id = hw["id"]

                if pinned_file_path == None:
                    clickable_pinned_file = "<i>Отсутствует</i>"
                else:
                    clickable_pinned_file = f'<a href="{pinned_file_path}">ТЫК</a>'


                if homework_file_path == None:
                    clickable_homework_file = "<i>Отсутствует</i>"
                else:
                    clickable_homework_file = f'<a href="{homework_file_path}">ТЫК</a>'

                if comment == None:
                    comment = "Отсутствует"

                if text_answer == None:
                    text_answer = "Отсутствует"


                pages_obj.add_page(f"""\
{homework_message_to_send}
Страница: №{pages_obj.page_count + 1} из {homework_count["type_1"]}

ДЗ по {lesson_name}:
Тема: <i>{theme}</i>
- Когда задали: <b>{start_date}</b>
- Сдано: <b>{done_date}</b>
- Оценка: <b>{mark}</b>
- ДЗ: {clickable_pinned_file}
- Выполненное ДЗ: {clickable_homework_file}
- Текстовый ответ: <i>{text_answer}</i>
Комментарий по дз от препода: <i>{comment}</i>

""", {"homework_id": homework_id, "lesson_name": lesson_name})

        case 2:
            homework_message_to_send = f"ДЗ, ожидающие проверки на <b>{today_date}:</b>\n\n"
            pages_count = homework_count["type_2"] // 6 + 2

            waited_homework: dict = get_user_status(telegram_id).API.get_homework(2, page)
            for hw in waited_homework:
                start_date = hw["creation_time"]
                end_date = hw["completion_time"]
                done_date = hw["homework_stud"]["creation_time"]

                lesson_name = hw["name_spec"]
                theme = hw["theme"]
                pinned_file_path = hw["file_path"]
                homework_file_path = hw["homework_stud"]["file_path"]
                homework_maded_id = hw["homework_stud"]["id"]
                text_answer = hw["homework_stud"]["stud_answer"]
                comment = hw["comment"]
                clickable_pinned_file = f'<a href="{pinned_file_path}">ТЫК</a>'

                homework_id = hw["id"]

                if pinned_file_path == None:
                    clickable_pinned_file = "<i>Отсутствует</i>"
                else:
                    clickable_pinned_file = f'<a href="{pinned_file_path}">ТЫК</a>'

                if homework_file_path == None:
                    clickable_homework_file = "<i>Отсутствует</i>"
                else:
                    clickable_homework_file = f'<a href="{homework_file_path}">ТЫК</a>'

                if text_answer == None:
                    text_answer = "Отсутствует"


                pages_obj.add_page(f"""\
Страница: №{pages_obj.page_count + 1} из {homework_count["type_2"]}
                                        
ДЗ по {lesson_name}:
Тема: <i>{theme}</i>
- Когда задали: <b>{start_date}</b>
- Сдано: <b>{done_date}</b>
- Крайний день: <b>{end_date}</b>
- ДЗ: {clickable_pinned_file}
- Выполненное ДЗ: {clickable_homework_file}
- Текстовый ответ: <i>{text_answer}</i>

""", {"homework_id": homework_id, "homework_maded_id": homework_maded_id})


        case 3:
            homework_message_to_send = f"Актуальное дз на <b>{today_date}:</b>\n\n"
            pages_count = homework_count["type_3"] // 6 + 2

            actual_homework: dict = get_user_status(telegram_id).API.get_homework(3, page)
            for hw in actual_homework:
                start_date = hw["creation_time"]
                end_date = hw["completion_time"]
                lesson_name = hw["name_spec"]
                theme = hw["theme"]
                pinned_file_path = hw["file_path"]
                banner_image_path = hw["cover_image"]
                comment = hw["comment"]

                homework_id = hw["id"]

                if comment == "":
                    comment = "Отсутствует"

                pages_obj.add_page(f"""\
Страница: №{pages_obj.page_count + 1} из {homework_count["type_3"]}

ДЗ по {lesson_name}:
Тема: <i>{theme}</i>
- Когда задали: <b>{start_date}</b>
- До какого надо сделать: <b>{end_date}</b>
- Прикрепленный файл: <a href="{pinned_file_path}">ТЫК</a>
Комментарий: <i>{comment}</i>

""", {"homework_id": homework_id, "lesson_name": lesson_name})
            

        case 5:
            homework_message_to_send = f"Отмененное дз на <b>{today_date}:</b>\n\n"
            pages_count = homework_count["type_5"] // 6 + 2

            actual_homework: dict = get_user_status(telegram_id).API.get_homework(5, page)
            for hw in actual_homework:
                start_date = hw["creation_time"]
                end_date = hw["completion_time"]
                lesson_name = hw["name_spec"]
                theme = hw["theme"]
                pinned_file_path = hw["file_path"]
                banner_image_path = hw["cover_image"]
                comment = hw["comment"]
                about_delete_comment = hw["homework_comment"]["text_comment"]

                homework_id = hw["id"]

                if comment == "":
                    comment = "Отсутствует"

                pages_obj.add_page(f"""\
Страница: №{pages_obj.page_count + 1} из {homework_count["type_5"]}

ДЗ по {lesson_name}:
Тема: <i>{theme}</i>
- Когда задали: <b>{start_date}</b>
- До какого надо сделать: <b>{end_date}</b>
- Прикрепленный файл: <a href="{pinned_file_path}">ТЫК</a>
Комментарий: <i>{comment}</i>
Комментарий по удаленной работе: <i>{about_delete_comment}</i>

""", {"homework_id": homework_id, "lesson_name": lesson_name})
    
    has_next_page = True if homework_count[f'type_{homework_type}'] > pages_obj.page_count else False

    if has_next_page:

        pages_obj.add_debug_page({"invoke_function": generate_homeworks_page, 
                              'invoke_function_args': [telegram_id, pages_obj, homework_type, page+1],
                              'has_next_page': has_next_page})


    return pages_obj

global bot
def setup_get_homework_module(bot: telebot.TeleBot):

    ### Отправить дз
    @bot.callback_query_handler(func= lambda call: "_homework_show" in call.data )
    @check_auth
    def call_get_homeworks(call: telebot.types.CallbackQuery):
        homework_type = int(call.data[0])
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) хочет посмотреть ДЗ под номером {homework_type}")
        
        homework_count = get_user_status(call.from_user.id).API.get_homework_count()

        if homework_count == 500:
            bot.send_message(call.message.chat.id, get_500_message(call.message))
            return
        
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
        turn_left_button, turn_right_button = make_turn_pages_buttons()
        keyboard.add(turn_left_button, turn_right_button)

        homework_type = int(call.data[0])
        
        if homework_type == 3 or homework_type == 0:
            send_homework_button = telebot.types.InlineKeyboardButton("📚 Сдать ДЗ", callback_data="send_homework_menu")
            keyboard.add(send_homework_button)


        elif homework_type == 5 or homework_type == 1:
            send_homework_button = telebot.types.InlineKeyboardButton("📚 Пересдать", callback_data="send_homework_menu")
            keyboard.add(send_homework_button)
        
        elif homework_type == 2:
            send_homework_button = telebot.types.InlineKeyboardButton("❌ Удалить", callback_data="delete_homework")
            keyboard.add(send_homework_button)

        keyboard.add(make_return_button())

        pages_obj = Pages()

        generate_homeworks_page(call.from_user.id, pages_obj=pages_obj, homework_type=homework_type, page=1)

        sended_message: telebot.types.Message = bot.send_message(
            call.message.chat.id, 
            pages_obj.get_page(), 
            parse_mode="HTML", 
            reply_markup=keyboard, 
            disable_web_page_preview=True)
        
        messages_pages[call.from_user.id].update({sended_message.message_id: pages_obj})
        logger.info(f"Пользователю ({call.from_user.username}:{call.from_user.id}) отправлено ДЗ под номером {call.data[0:1]}")

    ### Список ДЗ
    @bot.message_handler(func=lambda message: message.text == "📔 ДЗ")
    @check_auth
    def get_homework_menu(message: telebot.types.Message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) выбрал '{message.text}'")
        homework_count = get_user_status(message.from_user.id).API.get_homework_count()

        if homework_count == 500:
            bot.send_message(message.chat.id, get_500_message(message))
            return

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)


        homework0_button = telebot.types.InlineKeyboardButton(f"✖️ Просрок ({homework_count["type_0"]})", callback_data=f"0_homework_show")
        homework1_button = telebot.types.InlineKeyboardButton(f"✔️ Оцененное ({homework_count["type_1"]})", callback_data=f"1_homework_show")
        homework2_button = telebot.types.InlineKeyboardButton(f"⏳ На проверке ({homework_count["type_2"]})", callback_data=f"2_homework_show")
        homework3_button = telebot.types.InlineKeyboardButton(f"🖊 Актуальное ({homework_count["type_3"]})", callback_data=f"3_homework_show")
        homework5_button = telebot.types.InlineKeyboardButton(f"❔ Отмененное ({homework_count["type_5"]})", callback_data=f"5_homework_show")
        return_button = return_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="return_main")
        keyboard.add(homework0_button, homework1_button, homework2_button, homework3_button, homework5_button, return_button)

        bot.send_message(message.chat.id, "Выберите тип ДЗ которое вы хотите посмотреть:", reply_markup=keyboard)

