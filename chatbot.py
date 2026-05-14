import logging
import os
import threading

from dotenv import load_dotenv
from flask import Flask
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater
from waitress import serve

from ai_client import AIClient


# In-memory conversation history: {user_id: [messages]}
user_context: dict[int, list[dict]] = {}
MAX_HISTORY = 20  # keep last 20 messages (10 turns) per user
TELEGRAM_MESSAGE_CHUNK_SIZE = 4000  # Telegram limit is 4096; leave room for safety.

health_app = Flask(__name__)


@health_app.route("/")
def home():
    return "Bot is alive!"


def run_healthcheck() -> None:
    port = int(os.environ.get("PORT", 8080))
    logging.info("Starting healthcheck server on port %s", port)
    serve(health_app, host="0.0.0.0", port=port)


chatgpt: AIClient | None = None


def send_telegram_message(bot, chat_id: int, text: str) -> None:
    if not text:
        text = "AI 服务暂时没有返回内容。"

    for start in range(0, len(text), TELEGRAM_MESSAGE_CHUNK_SIZE):
        bot.send_message(chat_id=chat_id, text=text[start:start + TELEGRAM_MESSAGE_CHUNK_SIZE])


def equipped_chatgpt(update: Update, context: CallbackContext) -> None:
    global chatgpt

    if update.effective_chat is None or update.effective_user is None or update.message is None:
        logging.warning("Received an incomplete Telegram update: %s", update)
        return

    if chatgpt is None:
        logging.error("ChatGPT instance not initialized")
        send_telegram_message(context.bot, update.effective_chat.id, "服务暂时不可用，请稍后重试。")
        return

    user_id = update.effective_user.id
    user_msg = update.message.text or ""

    # Get or create conversation history for this user
    if user_id not in user_context:
        user_context[user_id] = []

    user_context[user_id].append({"role": "user", "content": user_msg})

    # Trim history to avoid token overflow
    if len(user_context[user_id]) > MAX_HISTORY:
        user_context[user_id] = user_context[user_id][-MAX_HISTORY:]

    reply_message = chatgpt.submit(user_context[user_id])

    user_context[user_id].append({"role": "assistant", "content": reply_message})

    logging.info("User %s: %s", user_id, user_msg)
    logging.info("Reply: %s", reply_message[:200])
    send_telegram_message(context.bot, update.effective_chat.id, reply_message)


def recommend(update: Update, context: CallbackContext) -> None:
    if context.args:
        interest = ' '.join(context.args)
    else:
        interest = None

    recommendations = {
        "online gaming": "Check out the upcoming tournament on GameZone!",
        "virtual reality": "Join the VR experience meetup at VirtualHub.",
        "social media": "Don't miss the social media trends webinar on SocialConnect."
    }
    if interest and interest.lower() in recommendations:
        update.message.reply_text(f"Recommendation for {interest}: {recommendations[interest.lower()]}")
    else:
        update.message.reply_text(
            "No recommendations available for that interest. Try 'online gaming', 'virtual reality', or 'social media'.")


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Available commands:\n'
                              '/help - Show this help message\n'
                              '/hello <name> - Greet the user\n'
                              '/recommend <interest> - Get event recommendations for an interest')


def hello(update: Update, context: CallbackContext) -> None:
    if context.args:
        name = context.args[0]
        update.message.reply_text(f"Good day, {name}!")
    else:
        update.message.reply_text("Hello! Please provide your name after the command.")


def main() -> None:
    # Load .env
    load_dotenv()

    # Setup logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Validate required config before starting background services.
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env or environment variables.")

    # Initialize ChatGPT instance (config from .env)
    global chatgpt
    chatgpt = AIClient()

    # Start healthcheck after loading env
    health_thread = threading.Thread(target=run_healthcheck, name="healthcheck", daemon=True)
    health_thread.start()

    # Initialize Telegram bot updater
    proxy_url = os.environ.get("PROXY_URL")
    request_kwargs = {"proxy_url": proxy_url} if proxy_url else {}
    updater = Updater(token=token, use_context=True, request_kwargs=request_kwargs)
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), equipped_chatgpt))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("recommend", recommend))

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
