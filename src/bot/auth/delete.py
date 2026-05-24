from ...storage import db_obj, settings_db_obj, user_auths, bot
from ..core.logs import logger

async def delete_user(user_id: int):
    chat = await bot.get_chat(chat_id=user_id)
    username = 'None'
    if chat.username:
        username = chat.username
    logger.info(f"Пользователь ({username}:{user_id}) выкинут из аккаунта")
    await db_obj.delete_user_by_telegram_id(user_id)
    await settings_db_obj.delete_settings_by_telegram_id(user_id)
    try:
        user_auths.pop(user_id)
    except:
        pass
    await bot.send_message(
        chat_id=user_id,
        text="Ваши данные от аккаунта неактуальны, перезайдите в бота")
