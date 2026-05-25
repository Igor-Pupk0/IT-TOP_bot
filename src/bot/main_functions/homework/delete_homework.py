import aiogram
from aiogram import F
from ...core.pages import Pages, messages_pages
from ...core.states import get_user_status

delete_homework_router = aiogram.Router()

@delete_homework_router.callback_query(F.data == "delete_homework")
async def delete_homework(call: aiogram.types.CallbackQuery):
    tmp = messages_pages.get(call.from_user.id)
    await call.answer()
    if tmp == None:
        await call.message.delete()
        return

    page_obj: Pages = tmp.get(call.message.message_id)
    
    if page_obj == None:
        await call.message.delete()
        return
            
    page_metadata = page_obj.get_page_metadata()
    homework_maded_id = page_metadata.get("homework_maded_id")

    res = await (get_user_status(call.from_user.id).API.delete_homework(homework_maded_id))

    if res:
        await call.message.answer(text="✅ ДЗ было удалено успешно")
    else:
        await call.message.answer(text="Дз не было удалено, попробуй еще раз")