import aiogram
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..auth.authorization_callbacks import check_auth
from ..core.logs import logger
from ..core.states import get_user_status
from ..core.keyboards import make_return_button
from ..core.pages import Pages, messages_pages
from ..core.journal_500 import get_500_message

leaderboards_router = aiogram.Router()

@leaderboards_router.callback_query(F.data == "show_leaderboards_menu")
@check_auth
async def handle_get_leaderboards(call: aiogram.types.CallbackQuery):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) смотрит лидерборды")
    pages_obj = Pages()
    
    stream_leaderboard = await get_stream_leaderboards(call)

    if stream_leaderboard == 500:
        await call.message.answer(text=get_500_message(call.message))
        return

    pages_obj.add_page(stream_leaderboard)
    pages_obj.add_page(await get_group_leaderboards(call))

    turn_left_button = aiogram.types.InlineKeyboardButton(text="👨‍👩‍👦 Поток",callback_data="turn_left")
    turn_right_button = aiogram.types.InlineKeyboardButton(text="🚹 Группа", callback_data="turn_right")
    keyboard = InlineKeyboardBuilder()
    
    keyboard.add(turn_left_button, turn_right_button, make_return_button())
    keyboard.adjust(2, 1)

    await call.answer()
    sended_message = await call.message.answer(
        text=pages_obj.get_page(), 
        parse_mode="HTML", 
        reply_markup=keyboard.as_markup(), 
        disable_web_page_preview=True)

    messages_pages[call.from_user.id].update({sended_message.message_id: pages_obj})

async def get_group_leaderboards(call: aiogram.types.CallbackQuery) -> str:
    group_peoples = await (get_user_status(call.from_user.id).API.get_leaderboard_group())

    leaderboard_message = 'Лидерборд группы:\n\n'

    for people in group_peoples:
        number = people["position"]
        full_name = people["full_name"]
        amount = people["amount"]
        photo_path = people["photo_path"]

        leaderboard_message += f"{number}) {amount}💰 <i>{full_name}</i> <a href='{photo_path}'>ФОТО</a>\n"

    return leaderboard_message
    

async def get_stream_leaderboards(call: aiogram.types.CallbackQuery) -> str:
    group_peoples = await (get_user_status(call.from_user.id).API.get_leaderboard_stream())

    leaderboard_message = 'Лидерборд потока:\n\n'

    for people in group_peoples:
        number = people["position"]
        full_name = people["full_name"]
        amount = people["amount"]
        photo_path = people["photo_path"]

        if full_name == None:
            leaderboard_message += '---------------------------------\n'
            continue

        leaderboard_message += f"{number}) {amount}💰 <i>{full_name}</i>, <a href='{photo_path}'>ФОТО</a>\n"
    
    return leaderboard_message

