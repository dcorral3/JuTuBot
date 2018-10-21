import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import TOKEN
from controller import Controller

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
C = Controller()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

start_handler = CommandHandler('start', C.start)
dispatcher.add_handler(start_handler)

url_handler = MessageHandler(Filters.text, C.url_message)
dispatcher.add_handler(url_handler)

updater.start_polling()
