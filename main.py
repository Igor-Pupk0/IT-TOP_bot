from src.bot.core.logs import logger

if __name__ == "__main__":
    logger.info("Бот запущен")
    from src.bot.main import bot
    bot.infinity_polling()