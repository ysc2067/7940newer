import configparser
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from ChatGPT_HKBU import HKBU_ChatGPT

config = configparser.ConfigParser()
config.read("config.ini")

telegram_token = config["TELEGRAM"]["TELEGRAM_TOKEN"].strip()
gemini_api_key = config["GEMINI"]["GEMINI_API_KEY"].strip()

chatgpt = HKBU_ChatGPT(gemini_api_key)

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot started！")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = chatgpt.chat(user_text)
    await update.message.reply_text(reply)

def main():
    application = ApplicationBuilder().token(telegram_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
