import logging
import configparser
from flask import Flask, request
from ChatGPT_HKBU import HKBU_ChatGPT
from telegram.ext import Updater, MessageHandler, Filters
import telegram

config = configparser.ConfigParser()
config.read("./config.ini")

telegram_token = config["TELEGRAM"]["TELEGRAM_TOKEN"].strip()
chatgpt = HKBU_ChatGPT(config)

app = Flask(__name__)

@app.route("/health")
def health():
    return "OK"

def reply(update, context):
    try:
        text = update.message.text
        resp = chatgpt.submit(text)
        update.message.reply_text(resp)
    except Exception as e:
        update.message.reply_text(str(e))

def main():
    updater = Updater(telegram_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, reply))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
