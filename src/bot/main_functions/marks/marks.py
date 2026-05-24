import aiogram
import aiogram
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from ...core.states import get_user_status
from ...auth.authorization_callbacks import check_auth
from .generate_html_marks import generate_marks_page
from ...core.keyboards import make_return_button
from ...core.logs import logger
from ...core.journal_500 import get_500_message

marks_router = aiogram.Router()

@marks_router.message(F.text == "5️⃣ Оценки")
@check_auth
async def send_marks_menu(message: aiogram.types.Message):
    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) хочет посмотреть оценки")
    marks = await (get_user_status(message.from_user.id).API.get_marks())
    if marks == 500:
        await message.answer(text=get_500_message(message))
        return
    elif type(marks) != list:
        await message.answer(text="Ошибка")
        return
    
    marks_page_url = await generate_marks_page(marks)
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(aiogram.types.InlineKeyboardButton(text='Открыть', web_app=aiogram.types.WebAppInfo(url=marks_page_url)))
    keyboard.add(make_return_button())
    await message.answer(text=f"Оценки готовы к просмотру", reply_markup=keyboard.as_markup())