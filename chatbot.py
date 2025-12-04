import configparser
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from ChatGPT_HKBU import HKBU_ChatGPT

config = configparser.ConfigParser()
config.read("config.ini")

telegram_token = config["TELEGRAM"]["TELEGRAM_TOKEN"].strip()
gemini_api_key = config["GEMINI"]["GEMINI_API_KEY"].strip()
model_name = config["GEMINI"].get("MODEL_NAME", "gemini-2.5-flash-lite").strip()

chatgpt = HKBU_ChatGPT(gemini_api_key, model_name)

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot start")


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
