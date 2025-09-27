from src.bot.core.logs import logger

if __name__ == "__main__":
    logger.info("Бот запущен")
    from src.bot.main import bot
    from src.bot.modules.webhooks import setup_webhooks_module
    try:
        setup_webhooks_module(bot)
    except Exception as e:
        logger.error(e)
        