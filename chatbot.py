from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
import configparser
import logging
import os
import supabase_db
from ChatGPT_HKBU import HKBU_ChatGPT
from flask import Flask
import threading

health_app = Flask(__name__)

@health_app.route("/")
def home():
    return "Bot is alive!"


def run_healthcheck():
    port = int(os.environ.get("PORT", 8080))
    health_app.run(host="0.0.0.0", port=port)

health_thread = threading.Thread(target=run_healthcheck)
health_thread.start()

global chatgpt, firebase_instance


def equipped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


def set_interest(update: Update, context: CallbackContext) -> None:
    if context.args:
        new_interest = ' '.join(context.args).strip()
        user_id = update.message.from_user.id

        # Check existing interest
        old_interest = firebase_instance.get_user_interest(user_id)

        if old_interest:
            firebase_instance.clear_user_interest(user_id)
            firebase_instance.set_user_interest(user_id, new_interest)
            update.message.reply_text(
                f"Your interest '{new_interest}' has replaced your previous interest '{old_interest}'."
            )
        else:
            firebase_instance.set_user_interest(user_id, new_interest)
            update.message.reply_text(f"Your interest '{new_interest}' has been saved.")
    else:
        update.message.reply_text("Usage: /setinterest <your interest>")


def match(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_interest = firebase_instance.get_user_interest(user_id)
    if not user_interest:
        update.message.reply_text("Please set your interest using the /setinterest command first.")
        return
    matched_users = firebase_instance.get_users_by_interest(user_interest)
    # Exclude current user from the result
    matched_users = [uid for uid in matched_users if uid != str(user_id)]
    if matched_users:
        update.message.reply_text(f"Users with similar interest ({user_interest}): " + ', '.join(matched_users))
    else:
        update.message.reply_text("No matching users found at the moment.")


def recommend(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if context.args:
        interest = ' '.join(context.args).strip()
    else:
        interest = firebase_instance.get_user_interest(user_id)
        if not interest:
            update.message.reply_text("You haven't provided or set any interest yet.")
            return

    prompt = (
        f"Please provide a personalized event or activity recommendation for a user "
        f"who is interested in '{interest}'. Keep it short and friendly."
    )

    response = chatgpt.submit(prompt)

    if response:
        update.message.reply_text(f"Here is a recommendation based on '{interest}':\n{response}")
    else:
        update.message.reply_text("Sorry, something went wrong while generating the recommendation.")



def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Available commands:\n'
                              '/help - Show this help message\n'
                              '/hello <name> - Greet the user\n'
                              '/setinterest <interest> - Set your interest\n'
                              '/match - Find users with similar interests\n'
                              '/recommend <interest> - Get event recommendations for an interest')

def clear_interest(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    interest = firebase_instance.get_user_interest(user_id)

    if not interest:
        update.message.reply_text("You have not set any interest yet.")
        return

    success = firebase_instance.clear_user_interest(user_id)
    if success:
        update.message.reply_text("Your interest has been cleared.")
    else:
        update.message.reply_text("Failed to clear your interest. Please try again later.")

def hello(update: Update, context: CallbackContext):
    if context.args:
        name = context.args[0]
        update.message.reply_text(f"Good day, {name}!")
    else:
        update.message.reply_text("Hello! Please provide your name after the command.")


def main():
    # Load configuration
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.ini')
    config = configparser.ConfigParser()
    config.read(config_path)

    # Setup logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Initialize Telegram bot updater
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    # Initialize ChatGPT instance using HKBU's API
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)

    # Initialize Firebase instance
    global firebase_instance
    firebase_instance = supabase_db.SupabaseDB()

    # Register handlers
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), equipped_chatgpt))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("setinterest", set_interest))
    dispatcher.add_handler(CommandHandler("match", match))
    dispatcher.add_handler(CommandHandler("recommend", recommend))
    dispatcher.add_handler(CommandHandler("clearinterest", clear_interest))

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
