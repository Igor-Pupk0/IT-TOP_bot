from functools import wraps
import aiogram
from src.api.Journal_API import API
from ...storage import db_obj, user_auths#, settings_db_obj
from ..core.states import get_user_status, delete_user_status
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..core.pages import messages_pages

def check_auth(func):
    @wraps(func)
    async def auth_check(message_or_call, *args, **kwargs):
        tmp = messages_pages.get(message_or_call.from_user.id)

        if tmp == None:
            messages_pages[message_or_call.from_user.id] = {}

        user_data = await db_obj.get_all_by_telegram_id(message_or_call.from_user.id)


        if user_auths.get(message_or_call.from_user.id) is None and user_data is not None:
            user_auths[message_or_call.from_user.id] = {
                "username": user_data[0],
                "password": user_data[1],
                "User_obj": API(user_data[0], user_data[1], user_data[2])
            }


        if user_data is None and message_or_call.from_user.id not in user_auths:
            markup = InlineKeyboardBuilder()
            markup.add(aiogram.types.InlineKeyboardButton(text="Вход", callback_data="init_auth"))
            await message_or_call.answer("Войди в аккаунт!", reply_markup=markup.as_markup())
            return

        if user_data and user_data[2] == 'None':
            await db_obj.update_user_JWT_token(user_data[0], user_auths[message_or_call.from_user.id]["User_obj"].JWT_TOKEN)

        return await func(message_or_call, *args, **kwargs)
    return auth_check

def load_user(func):
    @wraps(func)
    async def wrapper(bot, user_id: int):
        user_data = await db_obj.get_all_by_telegram_id(user_id)

        user_is_loaded = False
        if user_auths.get(user_id) is None and user_data is not None:
            user_is_loaded = True
            user_obj = API(user_data[0], user_data[1], user_data[2])
            await user_obj.init_user()
            user_auths[user_id] = {
                "username": user_data[0],
                "password": user_data[1],
                "User_obj": user_obj
            }


        if user_data and user_data[2] == 'None':
            await db_obj.update_user_JWT_token(user_data[0], user_auths[user_id]["User_obj"].JWT_TOKEN)

        try:
            await func(bot, user_id)
        finally:
            if user_is_loaded and user_id in user_auths:
                user_auths.pop(user_id)

        return 
    return wrapper
