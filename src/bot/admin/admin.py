import aiogram
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from ..core.keyboards import make_return_button
from .admin_funcs import check_on_dev
from .broadcast import broadcast_router

admin_router = aiogram.Router()
admin_router.include_router(broadcast_router)

@admin_router.message(Command('skibidi_admin'))
@check_on_dev
async def admin_panel(message: aiogram.types.Message):

    keyboard = InlineKeyboardBuilder()
    broadcast_button = aiogram.types.InlineKeyboardButton(text="📣 Broadcast", callback_data="admin_broadcast")

    keyboard.add(broadcast_button, make_return_button())
    keyboard.adjust(3)

    await message.answer(text="Админ панель", reply_markup=keyboard.as_markup())
