import telebot

def make_return_keyboard() -> telebot.types.InlineKeyboardMarkup :
    return_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    return_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="return")
    return_keyboard.add(return_button)
    return return_keyboard

def make_return_button() -> telebot.types.InlineKeyboardMarkup :
    return_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="return")
    return return_button

def make_turn_pages_buttons():
    turn_left_button = telebot.types.InlineKeyboardButton("⬅️ Влево",callback_data="turn_left")
    turn_right_button = telebot.types.InlineKeyboardButton("Направо ➡️", callback_data="turn_right")
    return turn_left_button, turn_right_button