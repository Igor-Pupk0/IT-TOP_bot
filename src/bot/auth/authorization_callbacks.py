###
### Тут реализована авторизация и проверка на нее
###

import aiogram
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F
from src.api.Journal_API import API
from ...storage import db_obj, settings_db_obj, user_auths
from .auth_funcs import check_auth
from ..core.logs import logger


class Auth_states(StatesGroup):
    waiting_login = State()
    waiting_password = State()
    nothing = State()

auth_router = aiogram.Router()

### Инициализация авторизации
@auth_router.callback_query(F.data == "init_auth")
async def user_auth(call: aiogram.types.CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) инициализировал процесс авторизации")
    await call.answer()
    user_data = await db_obj.get_all_by_telegram_id(call.from_user.id)

    if user_data != None:
        await call.message.answer("Ты уже авторизован!")
        return
    
    await state.set_state(Auth_states.waiting_login)
    await call.message.answer("Логин:")

### Авторизация
@auth_router.message(Auth_states.waiting_login)
async def auth_username(message: aiogram.types.Message, state: FSMContext):
    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел логин")
    username = message.text

    await state.set_state(Auth_states.waiting_password)
    await state.update_data(login=username)

    await message.answer("Пароль:")

@auth_router.message(Auth_states.waiting_password)
async def auth_password(message: aiogram.types.Message, state: FSMContext):
    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел пароль")
    
    data = await state.get_data()
    password = message.text
    login = data["login"]
    await state.set_state(Auth_states.nothing)
    user_api = API(login, password)
    await user_api.init_user()
    
    
    if user_api.succesful_auth == False:
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел неправильные данные для входа")
        await message.answer("Неправильные данные")
    else:
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) вошел в аккаунт")
        await message.answer("Успешный вход!")

        user_auths[message.from_user.id] = {}
        user_auths[message.from_user.id]['User_obj'] = user_api
        jwt_token = user_api.JWT_TOKEN
        await db_obj.insert_user_creds(message.from_user.id, username=login, password=password)
        await db_obj.update_user_JWT_token(login, jwt_token)
        await settings_db_obj.init_user_settings(message.from_user.id)


@auth_router.callback_query(F.data == "logout")
@check_auth
async def logout(call: aiogram.types.CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) вышел из аккаунта")
    await db_obj.delete_user_by_telegram_id(call.from_user.id)
    await settings_db_obj.delete_settings_by_telegram_id(call.from_user.id)
    await state.clear()
    user_auths.pop(call.from_user.id)
    await call.answer()
    await call.message.answer("Вы успешно вышли из аккаунта ✅")


