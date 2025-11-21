import telebot
import io

from ..authorization import check_auth
from ...core.pages import Pages, messages_pages
from ...core.logs import logger
from ...core.journal_500 import get_500_message
from ...core.states import get_user_status

homework_pages_data = {}

def setup_send_homework_module(bot: telebot.TeleBot):
    ### Отправить работу
    @bot.callback_query_handler(func= lambda call: "send_homework_menu" == call.data )
    @check_auth
    def call_send_homework_menu(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) хочет сдать ДЗ")


        user_homework_pages_data = homework_pages_data.get(call.from_user.id)
        if user_homework_pages_data != None:
            keyboard = telebot.types.InlineKeyboardMarkup()
            send_return_button = telebot.types.InlineKeyboardButton("🗑 Удалить меню", callback_data="return_and_delete_homework")
            keyboard.add(send_return_button)
            bot.send_message(call.message.chat.id, "Отрыть более 1 меню нельзя!", reply_markup=keyboard)
            return



        else:
            user_message_pages: dict = messages_pages.get(call.from_user.id)
            if user_message_pages == None:
                bot.delete_message(call.message.chat.id, call.message.id)
                return
            homework_page: Pages = user_message_pages.get(call.message.id)
            page_metadata: dict = homework_page.get_page_metadata()

            homework_data = {"homework_id": page_metadata["homework_id"], "lesson_name": page_metadata["lesson_name"]}

            keyboard, hw_message = make_homework_message(homework_data)

        

        bot.send_message(call.message.chat.id,
                            hw_message,
                            parse_mode="HTML",
                            reply_markup=keyboard)
        
        user_message_pages: dict = messages_pages.get(call.from_user.id)
        if user_message_pages == None:
            bot.delete_message(call.message.chat.id, call.message.id)
            return
        homework_page: Pages = user_message_pages.get(call.message.id)
        page_metadata: dict = homework_page.get_page_metadata()

        homework_pages_data[call.from_user.id] = {"homework_id": page_metadata["homework_id"], "lesson_name": page_metadata["lesson_name"]}
        

    @bot.callback_query_handler(func= lambda call: "write_answer_time" == call.data )
    @check_auth
    def call_write_time(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) вводит время для ДЗ")
        bot.send_message(call.message.chat.id, "Отправьте время в формате ЧЧ:ММ (час, минута. Пояснение для Стаса)",
                         reply_markup=make_cancel_keyboard())
        get_user_status(call.from_user.id).writing_time = True

    @bot.message_handler(func= lambda message: get_user_status(message.from_user.id).writing_time)
    @check_auth
    def get_writed_time(message: telebot.types.Message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел время: {message.text}")
        get_user_status(message.from_user.id).writing_time = False

        user_homework_pages_data = homework_pages_data.get(message.from_user.id)
        if user_homework_pages_data == None:
            bot.send_message(message.chat.id, "Ошибка, попробуйте запросить новое дз и через него снова сдать")
            return
        
        if len(message.text.split(":")) == 2 and '' not in message.text.split(":"):
            time = message.text.split(":")
            time_hrs, time_min = time

            if int(time_min) > 59 or int(time_min) < 1 or len(time_min) != 2:
                if not (int(time_min) == 0 and int(time_hrs) != 0):
                    bot.send_message(message.chat.id, "Неправильно установлены минуты")
                    return
            elif int(time_hrs) > 99 or int(time_hrs) < 0 or len(time_hrs) != 2:
                bot.send_message(message.chat.id, "Неправильно установлены часы")
                return
        else:
            bot.send_message(message.chat.id, "Неправильно установленое значение")
            return


        user_homework_pages_data.update({"homework_time": message.text})
        keyboard, hw_message = make_homework_message(user_homework_pages_data)
        bot.send_message(message.chat.id,
                        hw_message,
                        parse_mode="HTML",
                        reply_markup=keyboard)


    @bot.callback_query_handler(func= lambda call: "homework_write_text_answer" == call.data )
    @check_auth
    def call_write_text_answer(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) вводит текстовый ответ для ДЗ")
        bot.send_message(call.message.chat.id, "Отправьте свой ответ (лимит 1000 символов)",
                         reply_markup=make_cancel_keyboard())
        get_user_status(call.from_user.id).sending_text_answer = True

    @bot.message_handler(func= lambda message: get_user_status(message.from_user.id).sending_text_answer)
    @check_auth
    def get_sended_text_answer(message: telebot.types.Message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел текстовый ответ")
        get_user_status(message.from_user.id).sending_text_answer = False

        user_homework_pages_data = homework_pages_data.get(message.from_user.id)
        if user_homework_pages_data == None:
            bot.send_message(message.chat.id, "Ошибка, попробуйте запросить новое дз и через него снова сдать")
            return

        if len(message.text) > 1000:
            bot.send_message(message.chat.id, f"Ответ превышает лимит в 1000 символов (их {len(message.text)})")
            return
        
        user_homework_pages_data.update({"text_answer": message.text})
        bot.send_message(message.chat.id, "Текстовый ответ записан")
        keyboard, hw_message = make_homework_message(user_homework_pages_data)
        bot.send_message(message.chat.id,
                        hw_message,
                        parse_mode="HTML",
                        reply_markup=keyboard)


    @bot.callback_query_handler(func= lambda call: "homework_send_homework_file" == call.data )
    @check_auth
    def call_write_homework_file(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) хочет отправить файл к ДЗ")
        bot.send_message(call.message.chat.id, "Отправьте свой файл (Оправлять видео или фотокарточки файлом! Лимиты:\n - нельзя больше 99 мегабайт\n - Нельзя .txt и .csv файлы)",
                         reply_markup=make_cancel_keyboard())
        get_user_status(call.from_user.id).sending_homework_file = True

    @bot.message_handler(func= lambda message: get_user_status(message.from_user.id).sending_homework_file, content_types=['document'])
    @check_auth
    def get_sended_text_answer(message: telebot.types.Message):
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) отправил файл")
        get_user_status(message.from_user.id).sending_homework_file = False

        user_homework_pages_data = homework_pages_data.get(message.from_user.id)
        if user_homework_pages_data == None:
            bot.send_message(message.chat.id, "Ошибка, попробуйте запросить новое дз и через него снова сдать")
            return

        if message.content_type == "photo":
            homework_file_id = message.photo[-1].file_id
            homework_file = bot.get_file(homework_file_id)
        
        elif message.content_type == "video":
            homework_file = message.video.file_id

        else:
            homework_file = message.document

        FILE_99MB_SIZE_IN_BYTES = 830_472_192

        if homework_file.file_size > FILE_99MB_SIZE_IN_BYTES:
            bot.send_message(message.chat.id, f"Размер файла привышает 99 мегабайт")
            return

        if message.content_type != "photo":

            if ".txt" in homework_file.file_name or ".csv" in homework_file.file_name:
                bot.send_message(message.chat.id, "Недопустимый формат файла")
                return
        
        user_homework_pages_data.update({"homework_file_obj": homework_file})
        bot.send_message(message.chat.id, "Файл принят")
        keyboard, hw_message = make_homework_message(user_homework_pages_data)
        bot.send_message(message.chat.id,
                        hw_message,
                        parse_mode="HTML",
                        reply_markup=keyboard)
        
    @bot.callback_query_handler(func= lambda call: "send_homework" == call.data )
    @check_auth
    def call_checkout_homework(call: telebot.types.CallbackQuery):
        hw_data: dict = homework_pages_data.get(call.from_user.id)
        if hw_data == None:
            bot.send_message(call.message.chat.id, "Вы не заполнили все необходимые поля! (время, файл/текстовый ответ)")
            return
        

        text_answer = hw_data.get("text_answer")
        homework_time = hw_data.get("homework_time")
        homework_id = hw_data.get("homework_id")
        homework_file: telebot.types.Document = hw_data.get("homework_file_obj")
        homework_file_data = None
        if homework_file == None:
            homework_file = ''
        else:
            file_info = bot.get_file(homework_file.file_id)
            homework_file_name = homework_file.file_name
            file_bytes = bot.download_file(file_info.file_path)

            with io.BytesIO(file_bytes) as f:
                homework_file_data = f.read()

        if text_answer == None:
            text_answer = ""

        if text_answer == "" and homework_file == "":
            bot.send_message(call.message.chat.id, "Вы не заполнили все необходимые поля! (файл/текстовый ответ)")
            return

        if homework_time == None:
            bot.send_message(call.message.chat.id, "Вы не заполнили все необходимые поля! (время)")
            return

        if homework_id == None:
            bot.send_message(call.message.chat.id, "Ошибка, попробуйте запросить новое дз и через него снова сдать")
            return

        if homework_file_data == None:
            sended_request = get_user_status(call.from_user.id).API.send_homework(homework_id, text_answer, None, homework_time)
        else:
            sended_request = get_user_status(call.from_user.id).API.send_homework(homework_id, text_answer, homework_file_name, homework_time, homework_file_data)

        if sended_request == 500:
            bot.send_message(call.message.chat.id, "❗️Основной функционал бота недоступен из-за проблем со стороны основного журнала, попробуйте позже")
            return
        elif sended_request == 201:
            bot.send_message(call.message.chat.id, "Все успешно отправлено!")

        homework_pages_data.pop(call.from_user.id)

    
    @bot.callback_query_handler(func= lambda call: "homework_send_cancel" == call.data )
    @check_auth
    def call_cancel_sending_some(call: telebot.types.CallbackQuery):
        user = get_user_status(call.from_user.id)
        user.writing_time = False
        user.sending_text_answer = False
        user.sending_homework_file = False

        bot.delete_message(call.message.chat.id, call.message.id)
        

def make_cancel_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    cancel_button = telebot.types.InlineKeyboardButton("❌ Отмена", callback_data="homework_send_cancel")
    keyboard.add(cancel_button)
    return keyboard

def make_homework_message(hw_data: dict = None):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    write_text_answer_button = telebot.types.InlineKeyboardButton("🗒 Текстовый ответ", callback_data="homework_write_text_answer")
    send_homework_file_button = telebot.types.InlineKeyboardButton("📄 Файл", callback_data="homework_send_homework_file")
    write_time_button = telebot.types.InlineKeyboardButton("⏱️ Время на ДЗ", callback_data="write_answer_time")
    send_homework_to_server = telebot.types.InlineKeyboardButton("⬇️ Отправить", callback_data="send_homework")
    send_return_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="return_homework")

    keyboard.add(write_text_answer_button, 
                send_homework_file_button,
                write_time_button,
                send_homework_to_server,
                send_return_button)
    
    if hw_data == None:
        homework_time = "<i>Отсутствует</i>"
        text_answer = "<i>Отсутствует</i>"
        homework_file_name = "<i>Отсутствует</i>"
        lesson_name = "<i>Тип имя предмета</i>"
    else:
        text_answer = hw_data.get("text_answer")
        homework_time = hw_data.get("homework_time")
        lesson_name = hw_data.get("lesson_name")
        homework_file: telebot.types.Document = hw_data.get("homework_file_obj")
        if homework_file == None:
            homework_file_name = "<i>Отсутствует</i>"
        else:
            try:
                if homework_file.mime_type == "image/jpeg":
                    homework_file_name = "Фотокарточка.jpg"
            except AttributeError:
                homework_file_name = "Фотокарточка.jpg"
            else:
                homework_file_name = homework_file.file_name

    if text_answer == None:
        text_answer = "<i>Отсутствует</i>"

    if homework_time == None:
        homework_time = "<i>Отсутствует</i>"

    if lesson_name == None:
        lesson_name = "<i>Тип имя предмета</i>"


    message = f"""\
<b>Меню отправки ДЗ</b>
<b>{lesson_name}</b>

Прикрепленный файл: <i>{homework_file_name}</i>
Текстовый ответ: <i>{text_answer}</i>
Время: {homework_time}

<i>Что вы хотите изменить?</i>
"""

    return (keyboard, message)