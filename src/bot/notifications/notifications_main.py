from .almost_expired_homework import init_almost_expired_homework_notification
from ..core.logs import logger
import telebot

def init_notifications(bot: telebot.TeleBot):
    init_almost_expired_homework_notification(bot)


    logger.info("Все модули оповещений были загружены")