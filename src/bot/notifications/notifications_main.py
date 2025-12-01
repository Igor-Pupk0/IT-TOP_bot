from .almost_expired_homework import init_almost_expired_homework_notification
from ..core.logs import logger
import telebot
from ..core.storage import notification_scheduler

def init_notifications(bot: telebot.TeleBot):
    init_almost_expired_homework_notification(bot)


    notification_scheduler.start()

    logger.info("Все модули оповещений были загружены")