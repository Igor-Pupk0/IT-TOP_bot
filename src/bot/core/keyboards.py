import telebot

def make_return_keyboard() -> telebot.types.InlineKeyboardMarkup :
    return_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    return_button = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="return")
    return_keyboard.add(return_button)
    return return_keyboard