from dotenv import load_dotenv
import os
load_dotenv()
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import handlers
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables.")
        return

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("word", handlers.word_of_the_day))
    application.add_handler(CommandHandler("quiz", handlers.quiz))
    application.add_handler(CommandHandler("practice", handlers.practice))
    application.add_handler(CommandHandler("sentence", handlers.sentence_command))
    application.add_handler(CommandHandler("profile", handlers.profile_command))
    application.add_handler(CommandHandler("save", handlers.save_word_command))
    application.add_handler(CommandHandler("mywords", handlers.mywords_command))
    application.add_handler(CommandHandler("menu", handlers.menu_command))
    application.add_handler(CommandHandler("exit", handlers.exit_practice))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handlers.handle_message))

    print("Bot is running...")
    application.run_polling()





if __name__ == '__main__':
    main()
