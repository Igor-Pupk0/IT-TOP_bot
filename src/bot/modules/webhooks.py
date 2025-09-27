import telebot
from flask import Flask, request

WEBHOOK_URL = "https://DOMAIN_URL_PLACEHOLDER/it-top_bot"   # URL бота
CERT_PATH = "/etc/letsencrypt/live/DOMAIN_URL_PLACEHOLDER/"

app = Flask(__name__)

def setup_webhooks_module(bot: telebot.TeleBot):
    @app.route('/it-top_bot', methods=['POST'])
    def webhook():
        update = request.get_data().decode("utf-8")
        bot.process_new_updates([telebot.types.Update.de_json(update)])
        return "OK", 200
    
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL, )
    app.run(host="0.0.0.0", port=5000)