import aiogram
from ...storage import DEV_TELEGRAM_ID
from ..core.logs import logger
from functools import wraps

checked_admins = []

def check_on_dev(func):
    @wraps(func)
    async def wrapper(message: aiogram.types.CallbackQuery, *args, **kwargs):
        if message.from_user.id in checked_admins:
            return await func(message, *args, **kwargs)
        
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) проверяется на права админа")

        if DEV_TELEGRAM_ID == None:
            logger.warning(f"Администратор не указан")

        if int(DEV_TELEGRAM_ID) != message.from_user.id:
            await message.answer(text="Ты не админ")
            return
        
        logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) прошел проверку на админа")
        checked_admins.append(message.from_user.id)

        return await func(message, *args, **kwargs)
    
    return wrapper