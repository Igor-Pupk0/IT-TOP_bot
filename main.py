from src.bot.core.logs import logger
from src.bot.core.storage import ENV
from src.web.upload import app
import uvicorn
import asyncio

async def start_api():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def start_bot():
    from src.bot.bot_main import bot
    logger.info(f"Инициализация бота на профиле {ENV}")
    
    if ENV == "prod":
        from src.web.webhooks import setup_webhooks_module
        setup_webhooks_module(bot, app) 
    elif ENV == "dev":
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, bot.infinity_polling)

async def main():
    await asyncio.gather(
        start_api(),
        start_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())