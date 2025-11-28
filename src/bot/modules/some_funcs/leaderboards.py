import telebot
from ..authorization import check_auth
from ...core.logs import logger
from ...core.states import get_user_status
from ...core.keyboards import make_return_button
from ...core.keyboards import make_return_keyboard
from ...core.journal_500 import get_500_message

def setup_leaderboards_module(bot: telebot.TeleBot):
    @bot.callback_query_handler(func= lambda call: call.data == "show_leaderboards_menu")
    @check_auth
    def handle_get_leaderboards(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) смотрит лидерборды")

        message = "Какие лидерборды смотреть"

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        button_group_leaderboard = telebot.types.InlineKeyboardButton("🚹 Группа", callback_data="show_group_leaderboard")
        button_stream_leaderboard = telebot.types.InlineKeyboardButton("👨‍👩‍👦 Поток", callback_data="show_stream_leaderboard")
        keyboard.add(button_group_leaderboard, button_stream_leaderboard, make_return_button())

        bot.send_message(
            call.message.chat.id, 
            message, 
            parse_mode="HTML", 
            reply_markup=keyboard, 
            disable_web_page_preview=True)
        

    @bot.callback_query_handler(func= lambda call: call.data == "show_group_leaderboard")
    @check_auth
    def handle_group_leaderboards(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) смотрит лидерборд группы")
        group_peoples = get_user_status(call.from_user.id).API.get_leaderboard_group()
        if group_peoples == 500:
            bot.send_message(call.message.chat.id, get_500_message(call.message))
            return

        leaderboard_message = 'Лидерборд группы:\n\n'

        for people in group_peoples:
            number = people["position"]
            full_name = people["full_name"]
            amount = people["amount"]
            photo_path = people["photo_path"]

            leaderboard_message += f"{number}) {amount}💰 <i>{full_name}</i> <a href='{photo_path}'>ФОТО</a>\n"

        bot.send_message(call.message.chat.id,
                         leaderboard_message,
                         parse_mode="HTML",
                         disable_web_page_preview=True,
                         reply_markup=make_return_keyboard())
        

    @bot.callback_query_handler(func= lambda call: call.data == "show_stream_leaderboard")
    @check_auth
    def handle_stream_leaderboards(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) смотрит лидерборд потока")
        group_peoples = get_user_status(call.from_user.id).API.get_leaderboard_stream()
        if group_peoples == 500:
            bot.send_message(call.message.chat.id, get_500_message(call.message))
            return

        leaderboard_message = 'Лидерборд потока:\n\n'

        for people in group_peoples:
            number = people["position"]
            full_name = people["full_name"]
            amount = people["amount"]
            photo_path = people["photo_path"]

            if full_name == None:
                leaderboard_message += '---------------------------------------------------------------------\n'
                continue

            leaderboard_message += f"{number}) {amount}💰 <i>{full_name}</i>, <a href='{photo_path}'>ФОТО</a>\n"



        bot.send_message(call.message.chat.id,
                         leaderboard_message,
                         parse_mode="HTML",
                         disable_web_page_preview=True,
                         reply_markup=make_return_keyboard())



            

