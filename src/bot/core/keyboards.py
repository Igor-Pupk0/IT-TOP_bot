import aiogram
from aiogram.utils.keyboard import InlineKeyboardBuilder

def make_return_keyboard() -> aiogram.types.InlineKeyboardMarkup :
    return_keyboard = InlineKeyboardBuilder()
    return_button = aiogram.types.InlineKeyboardButton(text="🔙 Назад", callback_data="return")
    return_keyboard.add(return_button)
    return_keyboard.adjust(1)
    return return_keyboard.as_markup()

def make_return_button() -> aiogram.types.InlineKeyboardButton :
    return_button = aiogram.types.InlineKeyboardButton(text="🔙 Назад", callback_data="return")
    return return_button

def make_turn_pages_buttons():
    turn_left_button = aiogram.types.InlineKeyboardButton(text="⬅️",callback_data="turn_left")
    turn_right_button = aiogram.types.InlineKeyboardButton(text="➡️", callback_data="turn_right")
    return turn_left_button, turn_right_button