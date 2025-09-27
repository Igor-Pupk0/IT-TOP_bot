import telebot
import datetime

from ..core.storage import user_auths
from .authorization import check_auth
from ..core.pages import Pages, messages_pages
from ..core.keyboards import make_return_button, make_turn_pages_buttons
from ..core.logs import logger
from .journal_500 import check_server_error

def setup_homework_module(Bot):

    ### Отправить рассписание
    @Bot.callback_query_handler(func= lambda call: "_homework_show" in call.data )
    @check_auth
    def call_send_homework(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) хочет посмотреть ДЗ под номером {call.data[0:1]}")
        today_date = datetime.datetime.today().isoformat()[:10]
        homework_message_to_send = ''

        homework_count = user_auths[call.from_user.id]["User_obj"].get_homework_count()

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
        turn_left_button, turn_right_button = make_turn_pages_buttons()
        keyboard.add(turn_left_button, turn_right_button, make_return_button())

        pages_obj = Pages()

        match call.data:
            case "0_homework_show":
            #   homework: dict = user_auths[call.from_user.id]["User_obj"].get_homework(0, 1)
                
                pages_obj.add_page("В разработке")
                
            case "1_homework_show":
                homework_message_to_send = f"Оценки за дз на <b>{today_date}:</b>"
                pages_count = homework_count["type_1"] // 6 + 2

                for page in range(1, pages_count):
                    marked_homework = user_auths[call.from_user.id]["User_obj"].get_homework(1, page)


                    for hw in marked_homework:
                        start_date = hw["creation_time"]
                        done_date = hw["homework_stud"]["creation_time"]
                        lesson_name = hw["name_spec"]
                        theme = hw["theme"]
                        pinned_file_path = hw["file_path"]
                        homework_file_path = hw["homework_stud"]["file_path"]
                        mark = hw["homework_stud"]["mark"]
                        comment = hw["homework_comment"]["text_comment"]

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
    Комментарий по дз от препода: <i>{comment}</i>

    """)

            case "2_homework_show":
                homework_message_to_send = f"ДЗ, ожидающие проверки на <b>{today_date}:</b>\n\n"
                pages_count = homework_count["type_2"] // 6 + 2

                for page in range(1, pages_count):
                    waited_homework: dict = user_auths[call.from_user.id]["User_obj"].get_homework(2, page)
                    for hw in waited_homework:
                        start_date = hw["creation_time"]
                        end_date = hw["completion_time"]
                        done_date = hw["homework_stud"]["creation_time"]

                        lesson_name = hw["name_spec"]
                        theme = hw["theme"]
                        pinned_file_path = hw["file_path"]
                        homework_file_path = hw["homework_stud"]["file_path"]
                        comment = hw["comment"]
                        clickable_pinned_file = f'<a href="{pinned_file_path}">ТЫК</a>'

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

                        pages_obj.add_page(f"""\
Страница: №{pages_obj.page_count + 1} из {homework_count["type_2"]}
                                           
    ДЗ по {lesson_name}:
    Тема: <i>{theme}</i>
    - Когда задали: <b>{start_date}</b>
    - Сдано: <b>{done_date}</b>
    - Крайний день: <b>{end_date}</b>
    - ДЗ: {clickable_pinned_file}
    - Выполненное ДЗ: 
    Комментарий: <i>{comment}</i>
    
    """)


            case "3_homework_show":
                homework_message_to_send = f"Актуальное дз на <b>{today_date}:</b>\n\n"
                pages_count = homework_count["type_3"] // 6 + 2

                for page in range(1, pages_count):
                    actual_homework: dict = user_auths[call.from_user.id]["User_obj"].get_homework(3, page)
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

                        pages_obj.add_page(f"""\
Страница: №{pages_obj.page_count + 1} из {homework_count["type_3"]}

    ДЗ по {lesson_name}:
    Тема: <i>{theme}</i>
    - Когда задали: <b>{start_date}</b>
    - До какого надо сделать: <b>{end_date}</b>
    - Прикрепленный файл: <a href="{pinned_file_path}">ТЫК</a>
    Комментарий: <i>{comment}</i>

    """)
                
        sended_message: telebot.types.Message = Bot.send_message(
            call.message.chat.id, 
            pages_obj.get_page(), 
            parse_mode="HTML", 
            reply_markup=keyboard, 
            disable_web_page_preview=True)
        
        messages_pages[sended_message.message_id] = pages_obj
        logger.info(f"Пользователю ({call.from_user.username}:{call.from_user.id}) отправлено ДЗ под номером {call.data[0:1]}")




    ### Список ДЗ
    @Bot.message_handler(func=lambda message: message.text == "📔 Посмотреть ДЗ")
    @check_auth
    @check_server_error
    def check_homeworks(message: telebot.types.Message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) выбрал '{message.text}'")
        homework_count = user_auths[message.from_user.id]["User_obj"].get_homework_count()

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)


        homework0_button = telebot.types.InlineKeyboardButton(f"✖️ Просрок ({homework_count["type_0"]})", callback_data=f"0_homework_show")
        homework1_button = telebot.types.InlineKeyboardButton(f"✔️ Оцененное ({homework_count["type_1"]})", callback_data=f"1_homework_show")
        homework2_button = telebot.types.InlineKeyboardButton(f"⏳ На проверке ({homework_count["type_2"]})", callback_data=f"2_homework_show")
        homework3_button = telebot.types.InlineKeyboardButton(f"🖊 Актуальное ({homework_count["type_3"]})", callback_data=f"3_homework_show")
        return_button = return_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="return_main")
        keyboard.add(homework0_button, homework1_button, homework2_button, homework3_button, return_button)

        Bot.send_message(message.chat.id, "Выберите тип ДЗ которое вы хотите посмотреть:", reply_markup=keyboard)
