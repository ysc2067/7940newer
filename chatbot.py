from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
import logging
import os
from dotenv import load_dotenv
from ai_client import AIClient
from flask import Flask
from waitress import serve
import threading

# In-memory conversation history: {user_id: [messages]}
user_context: dict[int, list[dict]] = {}
MAX_HISTORY = 20  # keep last 20 messages (10 turns) per user

health_app = Flask(__name__)


@health_app.route("/")
def home():
    return "Bot is alive!"


def run_healthcheck() -> None:
    port = int(os.environ.get("PORT", 8080))
    serve(health_app, host="0.0.0.0", port=port)


chatgpt: AIClient | None = None


def equipped_chatgpt(update: Update, context: CallbackContext) -> None:
    global chatgpt
    if chatgpt is None:
        logging.error("ChatGPT instance not initialized")
        context.bot.send_message(chat_id=update.effective_chat.id, text="服务暂时不可用，请稍后重试。")
        return

    user_id = update.effective_user.id
    user_msg = update.message.text

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
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


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

    # Start healthcheck after loading env
    health_thread = threading.Thread(target=run_healthcheck)
    health_thread.start()

    # Initialize Telegram bot updater
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env or environment variables.")

    proxy_url = os.environ.get("PROXY_URL")
    request_kwargs = {"proxy_url": proxy_url} if proxy_url else {}
    updater = Updater(token=token, use_context=True, request_kwargs=request_kwargs)
    dispatcher = updater.dispatcher

    # Initialize ChatGPT instance (config from .env)
    global chatgpt
    chatgpt = AIClient()

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
