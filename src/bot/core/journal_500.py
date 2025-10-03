from .logs import logger
import telebot

def get_500_message(message: telebot.types.Message):
    message = telebot.types.Message(message.chat.id, "❗️Основной функционал бота недоступен из-за проблем со стороны основного журнала, попробуйте позже")
    logger.warning(f"Пользователь ({message.from_user.username}:{message.from_user.id}): Журнал не работает")
    return message