from src.bot.core.logs import logger
from src.storage import bot, db_obj, settings_db_obj
from src.bot.bot_main import dp
from src.bot.main_functions.marks.upload import app
from src.bot.notifications.notifications_main import init_notifications
import uvicorn
import asyncio

async def start_api():
    pass
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def start_bot():
    logger.info(f"Инициализация бота...")
    dp.startup.register(init_notifications)
    await dp.start_polling(bot)

async def main():
    await asyncio.gather(
        db_obj.init_db(),
        settings_db_obj.init_db(),
        start_api(),
        start_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())