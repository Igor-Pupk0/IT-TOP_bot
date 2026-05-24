import aiogram
from aiogram import F
from ..auth.authorization_callbacks import check_auth
from ..core.logs import logger
from ..core.states import get_user_status
from ..core.journal_500 import get_500_message

rate_lessons_router = aiogram.Router()

@rate_lessons_router.callback_query(F.data == "rate_all_lessons")
@check_auth
async def handle_rate_lessons(call: aiogram.types.CallbackQuery):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) хочет оценить все занятия")
    
    user = get_user_status(call.from_user.id)
    user_lessons = await user.API.get_lessons_for_feedback()
    await call.answer()
    if user_lessons == 500:
        await call.message.answer(text=get_500_message(call.message))
        return

    if user_lessons == []:
        await call.message.answer(text="Пар на оценку нет")
        return
    
    count = 0
    for lesson in user_lessons:
        await user.API.send_lesson_feedback(lesson.get("key"))
        count += 1

    
    await call.message.answer(text=
                              f"Было оценено <i>{count}</i> пар!", 
                                parse_mode="HTML")

