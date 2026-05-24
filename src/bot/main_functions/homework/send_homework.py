import aiogram
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import io

from ...auth.authorization_callbacks import check_auth
from ...core.pages import Pages, messages_pages
from ...core.logs import logger
from ...core.journal_500 import get_500_message
from ...core.states import get_user_status
from ....storage import homework_pages_data

send_homework_router = aiogram.Router()

class HomeWorkSendStates(StatesGroup):
    time = State()
    text = State()
    file = State()

### Отправить работу
@send_homework_router.callback_query("send_homework_menu" == F.data )
@check_auth
async def call_send_homework_menu(call: aiogram.types.CallbackQuery):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) хочет сдать ДЗ")

    await call.answer()

    user_homework_pages_data = homework_pages_data.get(call.from_user.id)
    if user_homework_pages_data != None:
        keyboard = InlineKeyboardBuilder()
        send_return_button = aiogram.types.InlineKeyboardButton(text="🗑 Удалить меню", callback_data="return_and_delete_homework")
        keyboard.add(send_return_button)
        await call.message.answer(text="Отрыть более 1 меню нельзя!", reply_markup=keyboard.as_markup())
        return

    else:
        user_message_pages: dict = messages_pages.get(call.from_user.id)
        if user_message_pages == None:
            await call.message.delete()
            return
        
        homework_page: Pages = user_message_pages.get(call.message.message_id)
        page_metadata: dict = homework_page.get_page_metadata()

        homework_data = {"homework_id": page_metadata["homework_id"], "lesson_name": page_metadata["lesson_name"]}

        keyboard, hw_message = make_homework_message(homework_data)


    await call.message.answer(text=hw_message,
                    parse_mode="HTML",
                    reply_markup=keyboard)
    
    user_message_pages: dict = messages_pages.get(call.from_user.id)
    if user_message_pages == None:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        return
    homework_page: Pages = user_message_pages.get(call.message.message_id)
    page_metadata: dict = homework_page.get_page_metadata()

    homework_pages_data[call.from_user.id] = {"homework_id": page_metadata["homework_id"], "lesson_name": page_metadata["lesson_name"]}
    

@send_homework_router.callback_query("write_answer_time" == F.data )
@check_auth
async def call_write_time(call: aiogram.types.CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) вводит время для ДЗ")
    await call.message.answer("Отправьте время в формате ЧЧ:ММ (час, минута)",
                        reply_markup=make_cancel_keyboard())
    
    await call.answer()
    await state.set_state(HomeWorkSendStates.time)

### Параметры для сдачи ДЗ
# self.sending_text_answer = False
# self.sending_homework_file = False

@send_homework_router.message(HomeWorkSendStates.time)
@check_auth
async def get_writed_time(message: aiogram.types.Message, state: FSMContext):
    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел время: {message.text}")
    await state.clear()

    user_homework_pages_data = homework_pages_data.get(message.from_user.id)
    if user_homework_pages_data == None:
        await message.answer(text="Ошибка, попробуйте запросить новое дз и через него снова сдать")
        return
    
    if len(message.text.split(":")) == 2 and '' not in message.text.split(":"):
        time = message.text.split(":")
        time_hrs, time_min = time

        if int(time_min) > 59 or int(time_min) < 1 or len(time_min) != 2:
            if not (int(time_min) == 0 and int(time_hrs) != 0):
                await message.answer(text="Неправильно установлены минуты")
                return
        elif int(time_hrs) > 99 or int(time_hrs) < 0 or len(time_hrs) != 2:
            await message.answer(text="Неправильно установлены часы")
            return
    else:
        await message.answer(text="Неправильно установленое значение")
        return


    user_homework_pages_data.update({"homework_time": message.text})
    keyboard, hw_message = make_homework_message(user_homework_pages_data)
    await message.answer(text=hw_message,
                    parse_mode="HTML",
                    reply_markup=keyboard)


@send_homework_router.callback_query("homework_write_text_answer" == F.data )
@check_auth
async def call_write_text_answer(call: aiogram.types.CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) вводит текстовый ответ для ДЗ")
    await call.message.answer(
        text="Отправьте свой ответ (лимит 1000 символов)",
        reply_markup=make_cancel_keyboard()
    )
    await call.answer()
    await state.set_state(HomeWorkSendStates.text)

@send_homework_router.message(HomeWorkSendStates.text)
@check_auth
async def get_sended_text_answer(message: aiogram.types.Message, state: FSMContext):
    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел текстовый ответ")
    await state.clear()

    user_homework_pages_data = homework_pages_data.get(message.from_user.id)
    if user_homework_pages_data == None:
        await message.answer(text="Ошибка, попробуйте запросить новое дз и через него снова сдать")
        return

    if len(message.text) > 1000:
        await message.answer(text=f"Ответ превышает лимит в 1000 символов (их {len(message.text)})")
        return
    
    user_homework_pages_data.update({"text_answer": message.text})
    await message.answer(text="Текстовый ответ записан")
    keyboard, hw_message = make_homework_message(user_homework_pages_data)
    await message.answer(
        text=hw_message,
        parse_mode="HTML",
        reply_markup=keyboard)


@send_homework_router.callback_query("homework_send_homework_file" == F.data )
@check_auth
async def call_write_homework_file(call: aiogram.types.CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) хочет отправить файл к ДЗ")
    await call.message.answer(text="Отправьте свой файл (Оправлять видео или фотокарточки файлом! Лимиты:\n - нельзя больше 99 мегабайт\n - Нельзя .txt и .csv файлы)",
                        reply_markup=make_cancel_keyboard())
    await call.answer()
    await state.set_state(HomeWorkSendStates.file)

@send_homework_router.message(HomeWorkSendStates.file)
@check_auth
async def get_sended_file(message: aiogram.types.Message, state: FSMContext):
    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) отправил файл")
    await state.clear()

    user_homework_pages_data = homework_pages_data.get(message.from_user.id)
    if user_homework_pages_data == None:
        await message.answer(text="Ошибка, попробуйте запросить новое дз и через него снова сдать")
        return

    if message.photo:
        file_id = message.photo[-1].file_id
        file_name = f"{file_id}.jpg"

    elif message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name

    FILE_99MB_SIZE_IN_BYTES = 830_472_192

    file_info = await message.bot.get_file(file_id)

    if file_info.file_size > FILE_99MB_SIZE_IN_BYTES:
        await message.answer(text=f"Размер файла привышает 99 мегабайт")
        return

    if ".txt" in file_name or ".csv" in file_name:
        await message.answer(text="Недопустимый формат файла")
        return
    
    
    user_homework_pages_data.update({"homework_file_obj": file_info})
    user_homework_pages_data.update({"file_name": file_name})
    await message.answer(text="Файл принят")
    keyboard, hw_message = make_homework_message(user_homework_pages_data)
    await message.answer(text=hw_message,
                    parse_mode="HTML",
                    reply_markup=keyboard)
    
@send_homework_router.callback_query("send_homework" == F.data)
@check_auth
async def call_checkout_homework(call: aiogram.types.CallbackQuery):
    hw_data: dict = homework_pages_data.get(call.from_user.id)
    await call.answer()
    if hw_data == None:
        await call.message.answer(text="Вы не заполнили все необходимые поля! (время, файл/текстовый ответ)")
        return
    

    text_answer = hw_data.get("text_answer")
    homework_time = hw_data.get("homework_time")
    homework_id = hw_data.get("homework_id")
    homework_file: aiogram.types.File = hw_data.get("homework_file_obj")
    homework_file_data = None
    if homework_file == None:
        homework_file = ''
    else:
        file_info = await call.message.bot.get_file(homework_file.file_id)
        file_name = hw_data.get("file_name")
        file_bytes = await call.message.bot.download_file(file_info.file_path)

        homework_file_data = file_bytes.read()

    if text_answer == None:
        text_answer = ""

    if text_answer == "" and homework_file == "":
        await call.message.answer(text="Вы не заполнили все необходимые поля! (файл/текстовый ответ)")
        return

    if homework_time == None:
        await call.message.answer(text="Вы не заполнили все необходимые поля! (время)")
        return

    if homework_id == None:
        await call.message.answer(text="Ошибка, попробуйте запросить новое дз и через него снова сдать")
        return

    if homework_file_data == None:
        sended_request = await (get_user_status(call.from_user.id).API.send_homework(homework_id, text_answer, None, homework_time))
    else:
        sended_request = await (get_user_status(call.from_user.id).API.send_homework(homework_id, text_answer, file_name, homework_time, homework_file_data))

    if not sended_request:
        await call.message.answer(text=get_500_message(call))
        return
    elif sended_request:
        await call.message.answer(text="Все успешно отправлено!")

    homework_pages_data.pop(call.from_user.id)


@send_homework_router.callback_query("homework_send_cancel" == F.data )
@check_auth
async def call_cancel_sending_some(call: aiogram.types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    

def make_cancel_keyboard():
    keyboard = InlineKeyboardBuilder()
    cancel_button = aiogram.types.InlineKeyboardButton(text="❌ Отмена", callback_data="homework_send_cancel")
    keyboard.add(cancel_button)
    return keyboard.as_markup()

def make_homework_message(hw_data: dict = None):
    keyboard = InlineKeyboardBuilder()
    write_text_answer_button = aiogram.types.InlineKeyboardButton(text="🗒 Текстовый ответ", callback_data="homework_write_text_answer")
    send_homework_file_button = aiogram.types.InlineKeyboardButton(text="📄 Файл", callback_data="homework_send_homework_file")
    write_time_button = aiogram.types.InlineKeyboardButton(text="⏱️ Время на ДЗ", callback_data="write_answer_time")
    send_homework_to_server = aiogram.types.InlineKeyboardButton(text="⬇️ Отправить", callback_data="send_homework")
    send_return_button = aiogram.types.InlineKeyboardButton(text="🔙 Назад", callback_data="return_homework")

    keyboard.add(write_text_answer_button, 
                send_homework_file_button,
                write_time_button,
                send_homework_to_server,
                send_return_button)
    
    keyboard.adjust(2)
    
    if hw_data == None:
        homework_time = "<i>Отсутствует</i>"
        text_answer = "<i>Отсутствует</i>"
        homework_file_name = "<i>Отсутствует</i>"
    else:
        text_answer = hw_data.get("text_answer")
        homework_time = hw_data.get("homework_time")
        lesson_name = hw_data.get("lesson_name")
        homework_file: aiogram.types.File = hw_data.get("homework_file_obj")
        file_name: str = hw_data.get("file_name")
        # if homework_file == None:
        #     homework_file_name = "<i>Отсутствует</i>"
        # else:
        #     try:
        #         if homework_file.file_path == "image/jpeg":
        #             homework_file_name = "Фотокарточка.jpg"
        #     except AttributeError:
        #         homework_file_name = "Фотокарточка.jpg"
        #     else:
        #         homework_file_name = homework_file.file_name

    if text_answer == None:
        text_answer = "<i>Отсутствует</i>"

    if homework_time == None:
        homework_time = "<i>Отсутствует</i>"

    if lesson_name == None:
        lesson_name = "<i>Тип имя предмета</i>"


    message = f"""\
<b>Меню отправки ДЗ</b>
<b>{lesson_name}</b>

Прикрепленный файл: <i>{file_name}</i>
Текстовый ответ: <i>{text_answer}</i>
Время: {homework_time}

<i>Что вы хотите изменить?</i>
"""

    return (keyboard.as_markup(), message)