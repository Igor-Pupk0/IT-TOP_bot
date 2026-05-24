import aiogram
from aiogram import F
from ..auth.authorization_callbacks import check_auth
from ..core.logs import logger
from ..core.states import get_user_status
from ..core.keyboards import make_return_keyboard
from ..core.journal_500 import get_500_message

exams_router = aiogram.Router()

@exams_router.callback_query(F.data == "show_future_exams")
@check_auth
async def handle_get_future_exams(call: aiogram.types.CallbackQuery):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) смотрит будущие экзмены")
    
    user = get_user_status(call.from_user.id)
    user_future_exams = await user.API.get_future_exams()
    if user_future_exams == 500:
        await call.message.answer(text=get_500_message(call))
        return

    message = 'Экзамены\n\n'
    for exam in user_future_exams:

        exam_name = exam["spec"]
        exam_date = exam["date"]
        message += f"  <i>{exam_date}</i> - <b>{exam_name}</b>\n"

    await call.answer()
    await call.message.answer(
        text=message, 
        parse_mode="HTML", 
        reply_markup=make_return_keyboard(), 
        disable_web_page_preview=True)