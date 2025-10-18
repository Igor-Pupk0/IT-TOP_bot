from src.bot.core.logs import logger
from src.bot.core.storage import ENV

if __name__ == "__main__":
    logger.info("Бот запущен")
    from src.bot.bot_main import bot
    try:
        if ENV == "prod":
            from src.bot.webhooks import setup_webhooks_module
            setup_webhooks_module(bot)
        elif ENV == "dev":
            bot.infinity_polling()
    except Exception as e:
        logger.error(f"Ошибка на профиле {ENV}: ", e)
        