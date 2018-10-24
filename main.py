import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import TOKEN
from controller import Controller
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
C = Controller()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

start_handler = CommandHandler('start', C.start)
dispatcher.add_handler(start_handler)

url_handler = MessageHandler(Filters.text, C.url_message)
dispatcher.add_handler(url_handler)


def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        print('Unauth')
        pass
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print('BadReq')
        pass
        # handle malformed requests - read more below!
    except TimedOut:
        print('TimeOut')
        pass
        # handle slow connection problems
    except NetworkError:
        print('NetworkErr')
        pass
        # handle other connection problems
    except ChatMigrated as e:
        print(str(e))
        pass
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print('TelegramError')
        pass
        # handle all other telegram related errors


dispatcher.add_error_handler(error_callback)

updater.start_polling()
