from ..auth.authorization_callbacks import check_auth
from .start import generate_start_message
import aiogram
from aiogram import F
from aiogram.fsm.context import FSMContext
from ...storage import homework_pages_data
from .states import get_user_status

return_router = aiogram.Router()

@return_router.callback_query(F.data.contains("return"))
@check_auth
async def menu_return(call: aiogram.types.CallbackQuery, state: FSMContext):
    await call.answer()
    if call.data == "return_main":
        text, keyboard = generate_start_message()
        await call.message.edit_text(text=text,
                                parse_mode="HTML")
        return
    
    match call.data:
        case "return_homework":
            if homework_pages_data.get(call.from_user.id) != None:
                homework_pages_data.pop(call.from_user.id)

        case "return_and_delete_homework":
            if homework_pages_data.get(call.from_user.id) != None:
                homework_pages_data.pop(call.from_user.id)
            
        case "return_state":
            await state.clear()
        
    await call.message.delete()