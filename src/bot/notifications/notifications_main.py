from .almost_expired_homework import init_almost_expired_homework_notification
from ..core.logs import logger
import aiogram
from ...storage import notification_scheduler

async def init_notifications(bot: aiogram.Bot):
    await init_almost_expired_homework_notification(bot)

    notification_scheduler.start()

    logger.info("Все модули оповещений были загружены")