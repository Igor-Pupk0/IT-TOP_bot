from .logs import logger
import telebot

def get_500_message(message_or_call: telebot.types.Message):
    message = telebot.types.Message(message_or_call.chat.id, "❗️Основной функционал бота недоступен из-за проблем со стороны основного журнала, попробуйте позже")
    logger.warning(f"Пользователь ({message_or_call.from_user.username}:{message_or_call.from_user.id}): Журнал не работает")
    return message