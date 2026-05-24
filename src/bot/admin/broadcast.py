import aiogram
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import exceptions
from ..core.logs import logger
from ...storage import db_obj, settings_db_obj
import asyncio
from .admin_funcs import check_on_dev

class BroadcastState(StatesGroup):
    wait_message = State()

broadcast_router = aiogram.Router()

@broadcast_router.callback_query("admin_broadcast" == F.data)
@check_on_dev
async def get_broadcast_message(call: aiogram.types.CallbackQuery, state: FSMContext):

    keyboard = InlineKeyboardBuilder()
    cancel_button = aiogram.types.InlineKeyboardButton(text="❌ Отмена", callback_data="return_state")
    keyboard.add(cancel_button)
    keyboard.adjust(1)
    await call.answer()
    await call.message.answer(text="Введи сообщение для броадкаста", reply_markup=keyboard.as_markup())
    await state.set_state(BroadcastState.wait_message)


@broadcast_router.message(BroadcastState.wait_message)
@check_on_dev
async def send_broadcast(message: aiogram.types.Message, state: FSMContext):
    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) вызвал broadcast")
    await state.clear()

    telegram_ids: tuple = await db_obj.get_all_telegram_ids()

    for id in telegram_ids:
        try:
            user_id = id[0]
            user_settings = await settings_db_obj.get_all_settings_by_telegram_id(user_id)

            if user_settings == None or type(user_settings) == int:
                continue

            if user_settings.get("get_admin_broadcasts") == 1:
                await message.copy_to(chat_id=user_id)
                await asyncio.sleep(0.05)
        
        except exceptions.TelegramForbiddenError:
            logger.warning(f"Пользователь {user_id} ограничил доступ к боту.")
            await settings_db_obj.delete_settings_by_telegram_id(user_id)

        except exceptions.TelegramBadRequest as e:
            logger.warning(f"Ошибка запроса для {user_id}: {e}")

        except Exception as e:
            logger.error(f"Непредвиденная ошибка при рассылке пользователю {user_id}: {e}", exc_info=True)

    await message.answer(text="✅ Broadcast успешно завершен")
