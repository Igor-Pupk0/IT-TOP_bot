import aiogram
from aiogram import F
from aiogram.exceptions import TelegramAPIError
from .pages import Pages, messages_pages, Keyboard_pages
from .logs import logger

page_callback_router = aiogram.Router()

@page_callback_router.callback_query(F.data.in_(["turn_left", "turn_right"]))
async def turn_pages(call: aiogram.types.CallbackQuery):
    tmp = messages_pages.get(call.from_user.id)
    await call.answer()

    if tmp == None:
        await call.message.delete()
        return

    page_obj = tmp.get(call.message.message_id)
    if type(page_obj) == Pages:
        if page_obj == None:
            await call.message.delete()
            return
                
        if call.data == "turn_right":
            turn_page = await page_obj.turn_right_page()

        elif call.data == "turn_left":
            turn_page = page_obj.turn_left_page()

        if turn_page == call.message.text or turn_page == False:
            return

        try:
            await call.message.edit_text(text=turn_page,
                                reply_markup=call.message.reply_markup,
                                parse_mode="HTML",
                                disable_web_page_preview=True)
        except TelegramAPIError:
            logger.warning(f"Пользователь ({call.from_user.username}:{call.from_user.id}): ошибка перевертыш")
            await turn_pages(call=call)
            
    elif type(page_obj) == Keyboard_pages:
        if page_obj == None:
            await call.message.delete()
            return
                
        if call.data == "turn_right":
            turn_page = page_obj.turn_right_page()

        elif call.data == "turn_left":
            turn_page = page_obj.turn_left_page()

        if turn_page == call.message.text or turn_page == False:
            return

        await call.message.edit_reply_markup(reply_markup=turn_page)