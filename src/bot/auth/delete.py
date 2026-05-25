from ...storage import db_obj, settings_db_obj, user_auths, bot, users_states, settings_pages, homework_pages_data
from ..core.logs import logger

async def delete_user(user_id: int, message_text: str = "Ваши данные от аккаунта неактуальны, перезайдите в бота"):
    chat = await bot.get_chat(chat_id=user_id)
    username = 'None'
    if chat.username:
        username = chat.username
    logger.info(f"Пользователь ({username}:{user_id}) вышел из аккаунта")
    await db_obj.delete_user_by_telegram_id(user_id)
    await settings_db_obj.delete_settings_by_telegram_id(user_id)
    try:
        user_auths.pop(user_id, None)
        users_states.pop(user_id, None)
        homework_pages_data.pop(user_id, None)
        settings_pages.pop(user_id, None)
        user_auths.pop(user_id, None)
    except:
        pass
    await bot.send_message(
        chat_id=user_id,
        text=message_text)
