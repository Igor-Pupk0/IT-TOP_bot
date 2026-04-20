import telebot
from fastapi import Request, Response
from ..bot.core.storage import WEBHOOK_DOMAIN, WEBHOOK_ENDPOINT

def setup_webhooks_module(bot: telebot.TeleBot, app):    
    @app.post(f"/{WEBHOOK_ENDPOINT}")
    async def webhook(request: Request):
        raw_update = await request.body()
        update_json = raw_update.decode("utf-8")
        
        update = telebot.types.Update.de_json(update_json)
        bot.process_new_updates([update])
        
        return Response(content="OK", status_code=200)

    bot.remove_webhook()
    webhook_url = f"https://{WEBHOOK_DOMAIN}/it-top_bot/{WEBHOOK_ENDPOINT}"
    bot.set_webhook(url=webhook_url)